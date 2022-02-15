#ifndef __SQUARE_ATTACK_H
#define __SQUARE_ATTACK_H

#include <stdint.h>
#include <stdbool.h>

bool check_guess(uint8_t* lambda_set, uint8_t key_guess, int byte_pos);

void inv_key_schedule(uint8_t* key, uint8_t* cipher_key, int round);

#endif // __SQUARE_ATTACK_H
