#ifndef __AES_H
#define __AES_H

#include <stdint.h>

/** Encrypts data using AES-128 cipher.
 *
 * msg[in]: Data to be encrypted (16 bytes).
 * key[in]: Key used for encryption (16 bytes).
 * encrypt_msg[out]: Long encrypted data (16 bytes).
 * rounds[in]: number of rounds
 */
void aes_encrypt(uint8_t* msg, uint8_t* key, uint8_t* encrypt_msg, int rounds);

#endif // __AES_H
