# Import necessary modules
import db
import utils

# Import the necessary C standard library header
from libc.stdlib cimport malloc, free

cimport cython

@cython.cdivision(True)
@cython.boundscheck(False)
@cython.wraparound(False)
@cython.nonecheck(False)

cpdef getAveragePriceForDate(str ticker, object date):
  cdef object response = db.getPriceForDate(ticker, date)
  if response is None or len(response) == 0:
    return -1

  cdef float price
  price = response[0][1]
  return price

cpdef getAveragePriceForWeek(str ticker, object initial_date, int weekNumber):
  cdef object current_date = utils.dateForWeek(initial_date, weekNumber)
  cdef float price = getAveragePriceForDate(ticker, current_date)
  return price

from libc.stdlib cimport malloc, free

cpdef processSingleRow(int sentiment, list symbs, object initDate, list accuracy_table, list alpha_table, list counts_table):
    cdef int process = True
    cdef int lastNoResponse = 0
    cdef int num_weeks = 50
    cdef float* accuracy_table_ptr = <float*>malloc(num_weeks * sizeof(float))
    cdef float* alpha_table_ptr = <float*>malloc(num_weeks * sizeof(float))
    cdef int* counts_table_ptr = <int*>malloc(num_weeks * sizeof(int))
    
    cdef int weekNumber
    cdef float initialPrice
    cdef float averageForWeek
    cdef float currentAlphaPoint
    cdef int currentAccuracyPoint
    cdef float writtenAccuracyPoints
    cdef float writtenAlphaPoints
    cdef int writtenCount
    cdef float summationForAccuracy
    cdef float summationForAlpha
    
    # Copy data to C arrays
    for i in range(num_weeks):
        accuracy_table_ptr[i] = accuracy_table[i+1]
        alpha_table_ptr[i] = alpha_table[i+1]
        counts_table_ptr[i] = counts_table[i+1]
    
    for symb in symbs:
        if '.' in symb:
            continue
        
        initialPrice = 41.7
        if initialPrice == -1 or initialPrice == 0:
            process = False
            break
        
        lastNoResponse = 0
        
        for weekNumber in range(1, num_weeks + 1):
            averageForWeek = 41.7
            
            if averageForWeek == -1:
                lastNoResponse += 1
                if lastNoResponse >= 2 and weekNumber - lastNoResponse == 1:
                    break
                continue
            
            writtenAccuracyPoints = accuracy_table_ptr[weekNumber - 1]
            writtenAlphaPoints = alpha_table_ptr[weekNumber - 1]
            writtenCount = counts_table_ptr[weekNumber - 1]

            currentAlphaPoint = sentiment * (averageForWeek - initialPrice) / initialPrice
            currentAccuracyPoint = 1 if currentAlphaPoint > 0 else -1

            summationForAccuracy = (writtenCount * writtenAccuracyPoints) + currentAccuracyPoint
            summationForAlpha = (writtenCount * writtenAlphaPoints) + currentAlphaPoint

            counts_table_ptr[weekNumber - 1] += 1
            accuracy_table_ptr[weekNumber - 1] = summationForAccuracy / counts_table_ptr[weekNumber - 1]
            alpha_table_ptr[weekNumber - 1] = summationForAlpha / counts_table_ptr[weekNumber - 1]

    # Copy results back to Python lists
    for i in range(num_weeks):
        accuracy_table[i] = accuracy_table_ptr[i]
        alpha_table[i] = alpha_table_ptr[i]
        counts_table[i] = counts_table_ptr[i]
    
    # Free allocated memory
    free(accuracy_table_ptr)
    free(alpha_table_ptr)
    free(counts_table_ptr)

    return process


cpdef unsigned long long int somefunc_cy3(long int K):    
    cdef unsigned long long int accum = 0
    cdef long int i    
    for i in range(K):
        if i % 5:
            accum = accum + i
    return accum


# cpdef processSingleRow(int sentiment, list symbs, object initDate, list accuracy_table, list alpha_table, list counts_table):
#     cdef int process = True
#     cdef int lastNoResponse = 0
#     cdef float initialPrice
#     cdef int weekNumber
#     cdef float averageForWeek
#     cdef float writtenAccuracyPoints
#     cdef float writtenAlphaPoints
#     cdef int writtenCount
#     cdef float currentAlphaPoint
#     cdef int currentAccuracyPoint
#     cdef float summationForAccuracy
#     cdef float summationForAlpha

#     for symb in symbs:
#         if '.' in symb:
#             continue
#         initialPrice = getAveragePriceForDate(symb, initDate)
#         if initialPrice == -1 or initialPrice == 0:
#             process = False
#             break
#         lastNoResponse = 0
#         for weekNumber in range(1, 51):
#             averageForWeek = getAveragePriceForWeek(symb, initDate, weekNumber)
#             if averageForWeek == -1:
#                 lastNoResponse += 1
#                 if lastNoResponse >= 2:
#                     if weekNumber - lastNoResponse == 1:
#                         break
#                 continue
#             writtenAccuracyPoints = accuracy_table[weekNumber]
#             writtenAlphaPoints = alpha_table[weekNumber]
#             writtenCount = counts_table[weekNumber]
#             currentAlphaPoint = sentiment * (averageForWeek - initialPrice) / initialPrice
#             currentAccuracyPoint = 1 if currentAlphaPoint > 0 else -1
#             summationForAccuracy = (writtenCount * writtenAccuracyPoints) + currentAccuracyPoint
#             summationForAlpha = (writtenCount * writtenAlphaPoints) + currentAlphaPoint
#             counts_table[weekNumber] += 1
#             accuracy_table[weekNumber] = summationForAccuracy / counts_table[weekNumber]
#             alpha_table[weekNumber] = summationForAlpha / counts_table[weekNumber]

#     return process, alpha_table, accuracy_table, counts_table


    

