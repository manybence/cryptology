#ifndef __SQUARE_ATTACK_H
#define __SQUARE_ATTACK_H

#include <stdint.h>
#include <stdbool.h>

/** Checks if a guess of one byte of the key is positive for a given
 * encrypted lambda_set.
 *
 * lambda_set[in]: Encrypted lambda set to try the gess against.
 * key_guess[in]: Key byte guess.
 * byte_pos[in]: Byte position to check.
 *
 * returns: bool, whether the guess fullfills the square attack rule and
 *          could be a good guess.
 */
bool check_guess(uint8_t* lambda_set, uint8_t key_guess, int byte_pos);

/** Given a round-key, it reverses the key shchedule algorithm a given
 * number of rounds to recover the original key.
 *
 * key[in]: The round-key.
 * cipher_key[out]: The recovered original key.
 * round[in]: The number of rounds to reverse.
 */
void inv_key_schedule(uint8_t* key, uint8_t* cipher_key, int round);

#endif // __SQUARE_ATTACK_H
