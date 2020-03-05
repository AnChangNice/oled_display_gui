

#include <stdio.h>
#include <stdint.h>



// Dither
extern __declspec(dllexport) int dithering(uint8_t* image, int w, int h, int bayer_size);

// Error diffusion
extern __declspec(dllexport) int error_diffusion(uint8_t* image, int w, int h);

// BW to bytes
typedef struct BW2BYTES_CONFIG_Type
{
	int flip_h;	// 0-not flip, 1-flip
	int flip_v;	// 0-not flip, 1-flip
	int scan_dir; // 0-Horizontal, 1-Vertical
	int byte_dir; // 0-Horizontal, 1-Vertical
	int sign_bit; // 0-MSB, 1-LSB
}bw2bytes_config_t;

extern __declspec(dllexport) int bw2Bytes(uint8_t* image, uint8_t* bytes, int w, int h, bw2bytes_config_t config);
