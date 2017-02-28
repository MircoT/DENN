#include <cmath>

namespace tensorflow
{
    template< class value_t = double > 
    class DEReset 
    {
    public:

        DEReset()
        : m_enable(false)
        , m_factor(100.0)
        , m_counter(0)
        , m_current_counter(0)
        , m_value((value_t)0)
        {
            
        }

        DEReset
        (
            bool    enable,
            value_t factor,
            int     counter,
            const NameList& rand_functions
        )
        : m_enable(enable)
        , m_factor(factor)
        , m_counter(counter)
        , m_rand_functions(rand_functions)
        , m_current_counter(0)
        , m_value((value_t)0)
        {
        }

        bool IsEnable() const
        { 
            return m_enable;
        }

        bool CanExecute(value_t value)
        {
            if(std::abs(m_value - value) < m_factor)
            {
                //dec counter
                ++m_current_counter;
                //test 
                if(m_counter <= m_current_counter)
                {
                    //reset 
                    m_current_counter = 0;
                    m_value = value;
                    //return true
                    return true;
                }
            }
            else 
            {
                //reset counter
                m_current_counter = 0;
            }
            //update value 
            m_value = value;
            //not reset
            return false;
        }

        const NameList& GetRandFunctions() const
        {
            return m_rand_functions;
        }

    protected:
        //const values
        bool     m_enable;
        value_t  m_factor;
        int      m_counter;   
        NameList m_rand_functions;         
        //runtime
        int     m_current_counter;
        value_t m_value;
    };

    template< class value_t = double > 
    class CacheBest
    {
    public:
        //add 
        bool test_best(value_t eval,int id, const TensorListList& pop)
        {
            //case to copy the individual
            if(!m_init || eval > m_eval)
            {
                //pop all
                m_individual.clear();
                //copy 
                for(const TensorList& layer : pop)
                {
                    m_individual.push_back(layer[id]);
                }
                //set init to true 
                m_init = true;
                m_eval = eval;
                m_id   = id;
                //is chanced
                return true;
            }
            return false;
        }
        
        //attrs
        bool       m_init{ false };
        int        m_id  { -1 };
        value_t    m_eval{  0 };
        TensorList m_individual;
    };
}