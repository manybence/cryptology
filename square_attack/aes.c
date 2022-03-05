#include <stdio.h>
#include <stdint.h>
#include <string.h>

#include "aes.h"
#include "constants.h"

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
}
