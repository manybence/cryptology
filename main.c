#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

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
uint8_t lambda_set[256][16];
uint8_t enc_lambda_set[256][16];
uint8_t guesses[16][256];
uint8_t guess_new[16][256];
bool single[16];
uint8_t solution[16];
bool done = false;

/** Function prototypes *******************************************************/
static void print_state(uint8_t* s);
static void merge_arrays(uint8_t* old, uint8_t* new_list);
static bool is_single(uint8_t* array);

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

static void merge_arrays(uint8_t* old, uint8_t* new_list){
    bool found = false;
    for (int i = 0; i < 256; i++){
        found = false;
        if (old[i] != (uint8_t)-1){
            for (int j = 0; j < 256; j++){
                if (old[i] == new_list[j]){
                    found = true;
                    break;
                }
            }
            if (!found) old[i] = -1;
        }
    }
    return;
}

static bool is_single(uint8_t* array){
    int size = 0;
    for (int i = 0; i < 256; i++){
        if (array[i] != (uint8_t)-1) size++;
    }
    return (size <= 1);
}

/** Main function *************************************************************/
int main(void)
{
    int pos = 0;
    // Generate lambda set
	lambda_set_generate((uint8_t*)lambda_set);

	// Encrypt lambda set
	for (int i = 0; i < 256; i++) {
		aes_encrypt((uint8_t*)lambda_set+i*16, key,
				(uint8_t*)enc_lambda_set+i*16, 4);
	}

    // Check first key byte (this is the 4th round key), store the guesses
    for (int i = 0; i < 16; i++) {
        pos = 0;
        for (int j = 0; j < 256; j++) {
            if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
                printf("Guess hit (%d): %02x\n", i, j);
                guesses[i][pos] = j;
                pos++;
            }
        }
    }

    //Initialize guess arrays
    for (int i = 0; i < 16; i++){
        single[i] = false;
        for (int j = 0; j < 256; j++){
            guesses[i][j] = -1;
            guess_new[i][j] = -1;
        }
    }
    bool done = false;

	// Generate lambda set
	lambda_set_generate((uint8_t*)lambda_set);

	// Encrypt lambda set
	for (int i = 0; i < 256; i++) {
		aes_encrypt((uint8_t*)lambda_set+i*16, key,
				(uint8_t*)enc_lambda_set+i*16, 4);
	}

    // Check first key byte (this is the 4th round key), store the guesses
    for (int i = 0; i < 16; i++) {
        pos = 0;
        for (int j = 0; j < 256; j++) {
            if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
                printf("Guess hit (%d): %02x\n", i, j);
                guesses[i][pos] = j;
                pos++;
            }
        }
    }

    while (!done){

        // Generate new lambda set
        sleep(1);
        lambda_set_generate((uint8_t*)lambda_set);

        // Encrypt new lambda set
        for (int i = 0; i < 256; i++) {
            aes_encrypt((uint8_t*)lambda_set+i*16, key,
                    (uint8_t*)enc_lambda_set+i*16, 4);
        }

        //Fill array with new guesses
        for (int i = 0; i < 16; i++) {
            pos = 0;
            for (int j = 0; j < 256; j++) {
                if (check_guess((uint8_t*)enc_lambda_set, j, i)) {
                    guess_new[i][pos] = j;
                    pos++;
                }
            }
        }

        //Display the stored guesses for each byte
        for (int i = 0; i < 16; i++){

            //Display original guesses
            printf("\nGuess (%d): ", i);
            for (int j = 0; j < 256; j++){
                if (guesses[i][j] != (uint8_t)-1)
                    printf("%02x, ", guesses[i][j]);
            }

            //Display new guesses
            printf("\nNew guesses (%d): ", i);
            for (int j = 0; j < 256; j++){
                if (guess_new[i][j] != (uint8_t)-1)
                    printf("%02x, ", guess_new[i][j]);
            }

            //Discard the wrong guesses, display the merged list
            merge_arrays(guesses[i], guess_new[i]);
            single[i] = is_single(guesses[i]);
            printf("\nMerged guesses (%d): ", i);
            for (int j = 0; j < 256; j++){
                if (guesses[i][j] != (uint8_t)-1)
                    printf("%02x, ", guesses[i][j]);
            }
            printf("single %d \n", single[i]);
        }

        //Check if there are multiple guesses
        done = true;
        for (int i = 0; i < 16; i++)
            if (single[i] == false) done = false;
    }

    if (done){
        //Assemble the key
        for (int i = 0; i < 16; i++){
            for (int j = 0; j < 256; j++){
                if (guesses[i][j] != (uint8_t)-1)
                    solution[i] = guesses[i][j];
            }
        }

        printf("\nSuccessful attack, the key is: ");
        for (int i = 0; i < 16; i++)
            printf("%02x", solution[i]);
    }

	return 0;
}
