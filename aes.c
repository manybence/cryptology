#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "aes.h"

/** Constants *****************************************************************/
static const uint8_t S[256] =
{
	0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
	0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
	0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
	0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
	0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
	0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
	0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
	0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
	0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
	0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
	0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
	0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
	0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
	0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
	0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
	0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16
};

static const uint8_t RCON[10] = {
	0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36
};

/** Function prototypes *******************************************************/
/* Galois multiplication by 1 */
static uint8_t gmult1(uint8_t factor);
/* Galois multiplication by 2 */
static uint8_t gmult2(uint8_t factor);
/* Galois multiplication by 3 */
static uint8_t gmult3(uint8_t factor);
/* Add round key step for a 128 bit (16 byte) block */
static void add_round_key(uint8_t* state, uint8_t* key);
/* Sub bytes step for a 128 bit (16 byte) block */
static void sub_bytes(uint8_t* state);
/* Shift rows step for a 128 bit (16 byte) block */
static void shift_rows(uint8_t* state);
/* Mix columns step for a 128 bit(16 byte) block */
static void mix_comlumns(uint8_t* state);
/* Retreive next round key from the previos one for a given round */
static void key_schedule(uint8_t* prev_key, uint8_t* new_key, int key_round);

/** AES mix columns constant matrix *******************************************/
typedef uint8_t (*galois_mult_t)(uint8_t);
static const galois_mult_t M[16] = 
{
	gmult2, gmult3, gmult1, gmult1,  /* 2 3 1 1 */
	gmult1, gmult2, gmult3, gmult1,  /* 1 2 3 1 */
	gmult1, gmult1, gmult2, gmult3,  /* 1 1 2 3 */
	gmult3, gmult1, gmult1, gmult2   /* 3 1 1 2 */
};

/** Function implementations **************************************************/
static uint8_t gmult1(uint8_t factor)
{
	return factor;
}

static uint8_t gmult2(uint8_t factor)
{
	uint8_t product = 0;
	if (factor & 0x80) {
		product = (factor << 1) ^ 0x11b;
	} else {
		product = factor << 1;
	}
	return product;
}

static uint8_t gmult3(uint8_t factor)
{
	return gmult2(factor) ^ factor;
}

static void add_round_key(uint8_t* state, uint8_t* key)
{
	for (int i = 0; i < 16; i++) {
		state[i] ^= key[i];
	}
}

static void sub_bytes(uint8_t* state)
{
	for (int i = 0; i < 16; i++) {
		state[i] = S[state[i]];
	}
}

static void shift_rows(uint8_t* state)
{
	uint8_t aux_state[16];
	memcpy(aux_state, state, 16);

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			state[i + j*4] = aux_state[i + ((j+i)*4 % 16)];
		}
	}
}

static void mix_comlumns(uint8_t* state)
{
	uint8_t aux_state[16];
	memcpy(aux_state, state, 16);

	for (int i = 0; i < 4; i++) {
		for (int j = 0; j < 4; j++) {
			state[i*4 + j] = 0;
			for (int k = 0; k < 4; k++) {
				state[i*4 + j] ^= M[j*4 + k](aux_state[i*4 + k]);
			}
		}
	}
}

static void key_schedule(uint8_t* prev_key, uint8_t* new_key, int key_round)
{
	uint8_t word[4];

	// rot word
	for (int i = 0; i < 4; i++) {
		word[i] = prev_key[12 + (i+1)%4];
	}
	
	// sub bytes word
	for (int i = 0; i < 4; i++) {
		word[i] = S[word[i]];
	}

	// Calculate first word of new key
	for (int i = 0; i < 4; i++) {
		new_key[i] = prev_key[i] ^ word[i%4];
	}

	// Add RCON to the first byte
	new_key[0] ^= RCON[key_round];

	// Calculate rest of new key
	for (int i = 4; i < 16; i++) {
		new_key[i] = prev_key[i] ^ new_key[i-4];
	}
}

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

/** Public functions **********************************************************/
void aes_encrypt(uint8_t* msg, uint8_t* key, uint8_t* encrypt_msg,
		int rounds)
{
	// Calculate round keys
	uint8_t keys[rounds][16];

	key_schedule(key, keys[0], 0);
	for (int i = 1; i < rounds; i++) {
		key_schedule(keys[i-1], keys[i], i);
	}
	
	// Copy initial state
	memcpy(encrypt_msg, msg, 16);

	// First add round key
	add_round_key(encrypt_msg, key);

	// 9 normal rounds
	for (int i = 0; i < rounds-1; i++) {
		sub_bytes(encrypt_msg);
		shift_rows(encrypt_msg);
		mix_comlumns(encrypt_msg);
		add_round_key(encrypt_msg, keys[i]);
	}

	// Last round
	sub_bytes(encrypt_msg);
	shift_rows(encrypt_msg);
	add_round_key(encrypt_msg, keys[rounds-1]);
	print_state(keys[rounds-1]);
}
