#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#include "square_attack.h"
#include "constants.h"

/** Function prototypes *******************************************************/
// Reverses AES last round (AddRoundKey and SubBytes)
static uint8_t reverse_last_round(uint8_t* enc_msg, uint8_t key_guess, int byte_pos);

/** Function implementations **************************************************/
static uint8_t reverse_last_round(uint8_t* enc_msg, uint8_t key_guess, int byte_pos)
{
	uint8_t result;

	// Reverse addRoundKey
	result = key_guess ^ enc_msg[byte_pos];

	// Reverse subBytes
	result = IS[result];

	return result;
}


/** Public functions **********************************************************/
bool check_guess(uint8_t* lambda_set, uint8_t key_guess, int byte_pos)
{
	uint8_t reverse_state[256];

	// Reverse last round for each byte
	for (int i = 0; i < 256; i++) {
		reverse_state[i] = reverse_last_round(lambda_set+i*16, key_guess, byte_pos);
	}

	// XOR every byte
	uint8_t sum = 0;
	for (int i = 0; i < 256; i++) {
		sum ^= reverse_state[i];
	}

	return sum == 0;
}

void inv_key_schedule(uint8_t* key, uint8_t* cipher_key, int rounds)
{
	uint8_t round_key[16];
	memcpy(round_key, key, 16);

	for (int round = rounds; round > 0; round--) {

		// Get the last word from previous key
		for (int i = 15; i >= 12; i--) {
			cipher_key[i] = round_key[i] ^ round_key[i-4];
		}

		// Now we have the last word from the previous key, we can calculate the
		// intermediate word

		uint8_t word[4];
		// rot word
		for (int i = 0; i < 4; i++) {
			word[i] = cipher_key[12 + (i+1)%4];
		}
		// sub bytes word
		for (int i = 0; i < 4; i++) {
			word[i] = S[word[i]];
		}	

		// Calculate first word of new key
		for (int i = 0; i < 4; i++) {
			cipher_key[i] = round_key[i] ^ word[i];
		}

		// Substract RCON to the first byte
		cipher_key[0] ^= RCON[round-1];

		// Calculate rest of the previous key
		for (int i = 4; i < 12; i++) {
			cipher_key[i] = round_key[i] ^ round_key[i-4];
		}

		memcpy(round_key, cipher_key, 16);
	}
}
