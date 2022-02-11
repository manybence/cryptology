#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "aes.h"
#include "lambda_set.h"
#include "square_attack.h"

/** Constants *****************************************************************/
static uint8_t msg[16] = {
	0x32, 0x43, 0xf6, 0xa8,
	0x88, 0x5a, 0x30, 0x8d,
	0x31, 0x31, 0x98, 0xa2,
	0xe0, 0x37, 0x07, 0x34
};

static uint8_t key[16] = {
	0x2b, 0x7e, 0x15, 0x16,
	0x28, 0xae, 0xd2, 0xa6,
	0xab, 0xf7, 0x15, 0x88,
	0x09, 0xcf, 0x4f, 0x3c
};

/** Global variables **********************************************************/
static uint8_t lambda_set[256][16];
static uint8_t enc_lambda_set[256][16];

/** Function prototypes *******************************************************/
static void print_state(uint8_t* s);

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

/** Main function *************************************************************/
int main(void)
{
	// Generate lambda set
	lambda_set_generate((uint8_t*)lambda_set);

	// Encrypt lambda set
	for (int i = 0; i < 256; i++) {
		aes_encrypt((uint8_t*)lambda_set+i*16, key,
				(uint8_t*)enc_lambda_set+i*16, 4);
	}

	// Check first key byte (this is the 4th round key)
	for (int i = 0; i < 16; i++) {
		for (int j = 0; j < 256; j++) {
			if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
				printf("Guess hit (%d): %02x\n", i, j);
			}
		}
	}

	return 0;
}
