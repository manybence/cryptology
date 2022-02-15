#include <stdio.h>
#include <stdint.h>

#include "aes.h"
#include "lambda_set.h"
#include "square_attack.h"


#define ROUNDS 4

/** Constants *****************************************************************/
static uint8_t key[16] = {
	0x2b, 0x7e, 0x15, 0x16,
	0x28, 0xae, 0xd2, 0xa6,
	0xab, 0xf7, 0x15, 0x88,
	0x09, 0xcf, 0x4f, 0x03
};

/** Global variables **********************************************************/
static uint8_t lambda_set[256][16];
static uint8_t enc_lambda_set[256][16];
static int16_t guesses[16][256];
static int16_t guess_new[16][256];
static uint8_t solution[16];
static bool done = false;

/** Function prototypes *******************************************************/
static void print_state(uint8_t* s);
static void merge_arrays(int16_t* old, int16_t* new_list);
static bool is_done(int16_t* array);

/** Function implementations **************************************************/
static void print_state(uint8_t* s)
{
	char aux[34];
	for (int i = 0; i < 16; i++) {
		sprintf(aux+i*2, "%02x", s[i]);
	}
	aux[32] = '\n';
	aux[33] = '\0';
	printf(aux);
}

static void merge_arrays(int16_t* old, int16_t* new_list)
{
	bool found;
	for (int i = 0; i < 256; i++) {
		if (old[i] != -1) {

			found = false;
			for (int j = 0; j < 256; j++) {
				if (old[i] == new_list[j]) {
					found = true;
					break;
				}
			}
			if (!found) {
				old[i] = -1;
			}

		}
	}
}

static bool is_done(int16_t* array)
{
	int size;
	for (int i = 0; i < 16; i++) {
		size = 0;
		for (int j = 0; j < 256; j++) {
			if (array[256*i + j] != -1) {
				size++;
			}
		}
		if (size > 1) {
			return false;
		}
	}
	return true;
}

/** Main function *************************************************************/
int main(void)
{
	lambda_set_seed_rng();

	printf("The cipher key is:             ");
	for (int i = 0; i < 16; i++) {
		printf("%02x", key[i]);
	}
	printf("\n");

	//Initialize guess arrays
	for (int i = 0; i < 16; i++) {
		for (int j = 0; j < 256; j++) {
			guesses[i][j] = -1;
			guess_new[i][j] = -1;
		}
	}


	/* First iteration of checking guesses */
	// Generate new lambda set
	lambda_set_generate((uint8_t*)lambda_set);

	// Encrypt new lambda set
	for (int i = 0; i < 256; i++) {
		aes_encrypt((uint8_t*)lambda_set+i*16, key,
				(uint8_t*)enc_lambda_set+i*16, ROUNDS);
	}

	// Fill array with guesses
	int pos;
	for (int i = 0; i < 16; i++) {
		pos = 0;
		for (int j = 0; j < 256; j++) {
			if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
				guesses[i][pos] = j;
				pos++;
			}
		}
	}


	/* Keep generating new guesses until there's only one per position */
	bool done = false;
	while (!done) {
		// Generate new lambda set
		lambda_set_generate((uint8_t*)lambda_set);

		// Encrypt new lambda set
		for (int i = 0; i < 256; i++) {
			aes_encrypt((uint8_t*)lambda_set+i*16, key,
					(uint8_t*)enc_lambda_set+i*16, ROUNDS);
		}

		// Fill array with new guesses
		for (int i = 0; i < 16; i++) {
			pos = 0;
			for (int j = 0; j < 256; j++) {
				if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
					guess_new[i][pos] = j;
					pos++;
				}
			}
		}

		// Compare guesses
		for (int i = 0; i < 16; i++) {
			merge_arrays(guesses[i], guess_new[i]);
		}

		// Check if done
		done = is_done((int16_t*)guesses);
	}

	// Assemble round key
	uint8_t round_key[16];
	for (int i = 0; i < 16; i++) {
		for (int j = 0; j < 256; j++) {
			if (guesses[i][j] != -1)
				round_key[i] = guesses[i][j];
		}
	}

	// Recover cipher key
	uint8_t cipher_key[16];
	inv_key_schedule(round_key, cipher_key, ROUNDS);

	printf("Successful attack, the key is: ");
	for (int i = 0; i < 16; i++) {
		printf("%02x", cipher_key[i]);
	}
	printf("\n");

	return 0;
}
