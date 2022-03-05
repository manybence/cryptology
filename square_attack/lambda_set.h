#ifndef __LAMBDA_SET_H
#define __LAMBDA_SET_H

#include <stdint.h>

/** Seeds the random number generator. */
void lambda_set_seed_rng(void);

/** Generate a 16 bytes long random key.
 *
 * key[out]: Pointer to where to store the key.
 */
void lambda_set_generate_key(uint8_t* key);

/** Generates new lambda set. A lambda set is a set of 256 messages, each of
 * them 16 bytes long. The data in each message is random, but it's the same for
 * all the messages, except for the first byte, which it's unique for each
 * message.
 *
 * p_lambda_set[out]: Pointer to where to store the set. It must be 256*16
 *                    (4096) bytes long.
 */
void lambda_set_generate(uint8_t* p_lambda_set);

#endif // __LAMBDA_SET_H
