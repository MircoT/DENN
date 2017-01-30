#include <config.h>
#include <dennop.h>

using namespace tensorflow;

REGISTER_OP("DENN")
.Attr("T: {float, double}")
.Attr("space: int")
.Attr("graph: string")
.Attr("CR: float = 0.5")
.Attr("f_min: float = -1.0")
.Attr("f_max: float = +1.0")
.Attr("f_inputs: list(string)")
.Attr("f_input_labels: string = 'y'")
.Attr("f_input_features: string = 'x'")
.Attr("f_name_execute_net: string = 'cross_entropy:0'")
.Attr("DE: {"
      "'rand/1/bin', "
      "'rand/1/exp', "
      "'rand/2/bin', "
      "'rand/2/exp',  "
      "'best/1/bin', "
      "'best/1/exp', "
      "'best/2/bin', "
      "'best/2/exp'  "
      "} = 'rand/1/bin'")
.Input("info: int32") //[ NUM_GEN, CALC_FIRST_EVAL ]
.Input("bach_labels: T")
.Input("bach_data: T")
.Input("population_first_eval: T")
.Input("w_list: space * T")
.Input("populations_list: space * T")
.Output("final_populations: space * T")
.Output("final_eval: T");


REGISTER_KERNEL_BUILDER(Name("DENN").Device(DEVICE_CPU).TypeConstraint<float>("T"), DENNOp<float>);
REGISTER_KERNEL_BUILDER(Name("DENN").Device(DEVICE_CPU).TypeConstraint<double>("T"), DENNOp<double>);
