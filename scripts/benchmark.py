##
# Only for testing
import sys
import signal
sys.path.append("../")
#####

import DENN
import tensorflow as tf

import numpy as np

from sys import argv
from time import sleep
from time import time
from datetime import datetime
from pytz import timezone
from tqdm import tqdm

# from memory_profiler import profile

# sleep(6)


class ENDict(dict):

    def __init__(self, *args, **kwargs):
        super(ENDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


class NDict(dict):
    pass


##
# Inhibit SIGHUP
# signal.siginterrupt(signal.SIGHUP, False)


#@profile
def main():
    ##
    # jobs
    jobs = []

    ##
    # datasets
    datasets = []

    jobs = DENN.training.open_task_list(argv[1])

    ##
    # Load data
    print("+ Load datasets")

    for job in jobs:
        datasets.append((DENN.training.Dataset(job.dataset_file), job))

    print("+ Start tests")
    time_start_test = time()

    for dataset, job in datasets:

        ##
        # Check Type
        assert job.TYPE == dataset.type, "Job type have to be equal to dataset type: {} != {}".format(job.TYPE, dataset.type)

        if job.training:
            ##
            # Ref:
            # https://docs.python.org/3/library/signal.html#signal.siginterrupt
            # False is needed to recover the execution
            signal.siginterrupt(signal.SIGINT, False)
            ##
            # Needed to stop background process on server
            # http://stackoverflow.com/questions/14696427/how-can-bash-script-do-the-equivalent-of-ctrl-c-to-a-background-task
            signal.siginterrupt(signal.SIGTERM, False)

        # print(job)

        time_start_dataset = time()

        ##
        # test data collections and options
        test_results = DENN.training.TestResults(job.de_types) 
        out_options = DENN.training.OutOptions(job, dataset.num_batches)

        prev_NN = dict(
            list(zip(job.de_types, [
                None for _ in range(len(job.de_types))]))
        )
        prev_F  = dict(
            list(zip(job.de_types, [
                None for _ in range(len(job.de_types))]))
        )
        prev_CR = dict(
            list(zip(job.de_types, [
                None for _ in range(len(job.de_types))]))
        )

        cur_nn = job.gen_network(True)

        with cur_nn.graph.as_default() as cur_graph:

            ##
            # Write output graph
            writer = tf.summary.FileWriter(logdir='logdir', graph=cur_graph)
            writer.flush()
            writer.close()
            tf.train.write_graph(cur_graph, 'graphs/', '{}.pbtxt'.format(job.name))

            session_config = tf.ConfigProto(
                intra_op_parallelism_threads=job.num_intra_threads,
                inter_op_parallelism_threads=job.num_inter_threads,
                # log_device_placement=True
                log_device_placement=False
            )

            ##
            # Needed by training task
            start_job = time()

            with tf.Session(config=session_config) as sess:

                denn_operators = {}

                time_node_creation = time()

                for de_type in job.de_types:

                    ## 
                    # Init F 
                    cur_f = sess.run(cur_nn.F_init)
                    prev_F[de_type] = cur_f

                    ##
                    # Init CR 
                    cur_cr = sess.run(cur_nn.CR_init)
                    prev_CR[de_type] = cur_cr

                    ##
                    # Random initialization of the NN
                    cur_pop = sess.run(cur_nn.rand_pop)

                    ##
                    # Initial population insertion
                    for level in job.levels:
                        for elm_idx, elem in enumerate(level.start_transposed):
                            for ind_pos, individual_elm in enumerate(elem):
                                cur_pop[elm_idx][ind_pos] = np.array(individual_elm)

                    ##
                    # Initial population insertion (individuals)
                    for level in job.levels:
                        for ind_pos, individual in enumerate(level.start):
                            for elm_idx, elem in enumerate(individual):
                                cur_pop[elm_idx][ind_pos] = np.array(elem)


                    prev_NN[de_type] = cur_pop
                    
                    with tf.device("/cpu:0"):
                        ##
                        # DENN op
                        denn_operators[de_type] = DENN.Operation(
                            dataset, job, cur_nn, de_type)

                print(
                    "++ Node creation {}".format(time() - time_node_creation))

                for de_type, denn_op in denn_operators.items():

                    ##
                    # Do first evaluation
                    evaluations = []

                    for idx in range(job.NP):
                        cur_evaluation = sess.run(cur_nn.accuracy, feed_dict=dict(
                            [
                                (target, cur_pop[num][idx])
                                for num, target in enumerate(cur_nn.targets)
                            ]
                            +
                            [
                                (cur_nn.label_placeholder,
                                 dataset.validation_labels),
                                (cur_nn.input_placeholder,
                                 dataset.validation_data)
                            ]
                        ))
                        evaluations.append(cur_evaluation)

                    best_idx = np.argmin(evaluations)

                    cur_accuracy = sess.run(cur_nn.accuracy, feed_dict=dict(
                        [
                            (target, cur_pop[num][best_idx])
                            for num, target in enumerate(cur_nn.targets)
                        ]
                        +
                        [
                            (cur_nn.label_placeholder, dataset.test_labels),
                            (cur_nn.input_placeholder, dataset.test_data)
                        ]
                    ))

                    test_results[de_type].values.append(cur_accuracy)

                    DENN.update_best_of(
                        de_type,
                        test_results,
                        cur_accuracy,
                        evaluations[best_idx],
                        cur_f,
                        cur_cr,
                        [
                            cur_pop[num][best_idx] for num, target in enumerate(cur_nn.targets)
                        ],
                        job
                    )

                    ##
                    # Do evolution
                    denn_op.run(sess, prev_F, prev_CR, prev_NN, test_results, {
                        'start_job': start_job
                    })

                    ##
                    # Reset AdaBoost cache
                    job.reset_adaboost_cache()

        print("+ Completed all test on dataset {} in {} sec.".format(job.name,
                                                                     time() - time_start_dataset))
        print("+ Save results for {}".format(job.name))

        description = "NP: {}  F: {}  CR: {}".format(
            job.NP,
            job.F,
            job.CR
        )

        job.time = time() - time_start_test

        write_results_time = datetime.now(timezone('Europe/Rome'))

        DENN.training.export_results(test_results, int(
            job.GEN_STEP / job.GEN_SAMPLES),
            job.name, out_options,
            folderByTime=write_results_time
        )

        DENN.training.expand_results(
            test_results, int(job.GEN_STEP / job.GEN_SAMPLES), job.de_types)

        DENN.training.write_all_results(
            job.name, test_results, description, out_options,
            folderByTime=write_results_time
        )

        tf.reset_default_graph()

    print("+ Completed all test {} sec.".format(time() - time_start_test))


if __name__ == '__main__':
    main()
