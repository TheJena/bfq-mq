/*
 * Macros to measure time deltas in a really rough way
 *
 * Usage:
 * - include "bfq-mq-time-deltas.h"
 * - define TIME_DELTAS_ON macro
 * - define the needed TIME_DELTA_PRINT_* macro(s)
 * - in the function which contains the code to measure:
 *   - initialize N measures with TIME_DELTAS_INIT(N)
 *   - wrap each one of the N pieces of code to measure like:
 *     TIME_DELTA_RECORD_START;
 *     <code to measure>
 *     TIME_DELTA_RECORD_STOP("name_to_print");
 *
 * A WARN message should occur when:
 * - you insert more than N start/stop macros
 * - you add start/stop macros in an unbalanced way
 */

/*
 * Enable TIME_DELTAS* macros and disable bfq_log_* macros
 */
#define TIME_DELTAS_ON

/*
 * Print the time needed to execute the
 * measured piece of code (t_delta [ns])
 */
#define TIME_DELTA_PRINT_DURATIONS

/*
 * Print the total cumulative execution time
 * of the measured piece of code (t_tot [ns]), and
 * the number of times it has been executed (calls)
 */
#define TIME_DELTA_PRINT_TOTAL_TIME_AND_CALLS

#ifdef TIME_DELTAS_ON
    #define TIME_DELTA_RECORD_PREFIX_FMT "%27s +%4d %-42s "
    #define TIME_DELTA_RECORD_PREFIX __FILE__, __LINE__
#endif

#if defined(TIME_DELTAS_ON) && defined(TIME_DELTA_PRINT_DURATIONS)
    #define TIME_DELTA_PRINT_DURATION(record_name) do {		      \
	trace_printk(TIME_DELTA_RECORD_PREFIX_FMT "%8s %9llu %2s\n",	      \
		     TIME_DELTA_RECORD_PREFIX, record_name,		      \
		     "t_delta:", my_t_ns[my_i], "ns");			      \
    } while (0)
#else
    #define TIME_DELTA_PRINT_DURATION(record_name)
#endif

#if defined(TIME_DELTAS_ON) && defined(TIME_DELTA_PRINT_TOTAL_TIME_AND_CALLS)
    #define TIME_DELTA_PRINT_T_TOT_AND_CNT(record_name) do {		      \
	trace_printk(TIME_DELTA_RECORD_PREFIX_FMT "%8s %9llu %2s, %8s %9u\n", \
		     TIME_DELTA_RECORD_PREFIX, record_name,		      \
		     "t_tot:", my_t_tot[my_i], "ns",			      \
		     "calls:", my_cnt[my_i]);				      \
    } while (0)
#else
    #define TIME_DELTA_PRINT_T_TOT_AND_CNT(record_name)
#endif

#ifdef TIME_DELTAS_ON
    #define TIME_DELTA_START true
    #define TIME_DELTA_STOP false
    #define TIME_DELTAS_INIT(i)					      \
	u64 my_t_ns[i];							      \
	unsigned int my_i=0;						      \
	static u64 my_t_tot[i];						      \
	static unsigned int my_cnt[i];					      \
	bool my_expected_start = true;
    #define TIME_DELTA_CHECK(my_start)				      \
	if (my_start != my_expected_start)				      \
		trace_printk(TIME_DELTA_RECORD_PREFIX_FMT "\n",		      \
			     TIME_DELTA_RECORD_PREFIX, "WARNING"	      \
			     " unbalanced TIME_DELTA_RECORD_[START|STOP]");   \
	my_expected_start = !my_expected_start;				      \
	if (my_i >= sizeof(my_t_ns) / sizeof(u64)) {			      \
	    if (!my_start) {						      \
		trace_printk(TIME_DELTA_RECORD_PREFIX_FMT "%8s %s(%u)  %8s\n",\
			     TIME_DELTA_RECORD_PREFIX,			      \
			     "WARNING array index out of bounds!",	      \
			     "set:", "TIME_DELTAS_INIT", my_i + 1, "please!");\
		my_i++;							      \
	    }								      \
	    break;							      \
	}
    #define TIME_DELTA_RECORD_START do {				      \
	TIME_DELTA_CHECK(TIME_DELTA_START);				      \
	my_cnt[my_i]++;							      \
	my_t_ns[my_i] = ktime_get_ns();					      \
    } while (0)
    #define TIME_DELTA_RECORD_STOP(record_name) do {			      \
	TIME_DELTA_CHECK(TIME_DELTA_STOP);				      \
	my_t_ns[my_i] = ktime_get_ns() - my_t_ns[my_i];			      \
	my_t_tot[my_i] += my_t_ns[my_i];				      \
	TIME_DELTA_PRINT_DURATION(record_name);				      \
	TIME_DELTA_PRINT_T_TOT_AND_CNT(record_name);			      \
	my_i++;								      \
    } while (0)

    // redefine logging macros to make them quiet and avoid unused var warnings
    #undef bfq_log_bfqq
    #undef bfq_log_bfqg
    #undef bfq_log
    #define bfq_log_bfqq(bfqd, bfqq, fmt, args...)	((void) (bfqq))
    #define bfq_log_bfqg(bfqd, bfqg, fmt, args...)	((void) (bfqg))
    #define bfq_log(args...)

#else
    #define TIME_DELTAS_INIT(i)
    #define TIME_DELTA_RECORD_START
    #define TIME_DELTA_RECORD_STOP(record_name)
#endif
