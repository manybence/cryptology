#ifndef __LAMBDA_SET_H
#define __LAMBDA_SET_H

#include <stdint.h>

/** Generates new lambda set. A lambda set is a set of 256 messages, each of
 * them 16 bytes long. The data in each message is random, but it's the same for
 * all the messages, except for the first byte, which it's unique for each
 * message.
 *
 * p_lambda_set[out]: Ponter where to store the set, must be 256*16 (4096)
 *                    bytes long.
 */
void lambda_set_generate(uint8_t* p_lambda_set);

#endif // __LAMBDA_SET_H
