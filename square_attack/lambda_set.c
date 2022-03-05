#include <time.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

/** Function prototypes *******************************************************/
static void generate_random_data(uint8_t* data, size_t size);

/** Function implementations **************************************************/
static void generate_random_data(uint8_t* data, size_t size)
{
	for (int i = 0; i < size; i++) {
		data[i] = rand() % 0xff;
	}
}

/** Public functions **********************************************************/
void lambda_set_seed_rng(void)
{
	time_t t;
	srand((unsigned) time(&t));
}

void lambda_set_generate_key(uint8_t* key)
{
	generate_random_data(key, 16);
}

void lambda_set_generate(uint8_t* p_lambda_set)
{
	uint8_t random_data[16];
	generate_random_data(random_data, sizeof(random_data));

	for (int i = 0; i < 256; i++) {
		memcpy(p_lambda_set+i*16, random_data, 16);
		p_lambda_set[i*16] = i;
	}
}
