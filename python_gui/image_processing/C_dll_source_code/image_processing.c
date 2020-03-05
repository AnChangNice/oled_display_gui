
#include "image_processing.h"

#include <malloc.h>

// Macro
#define XY(x, y, w)							(x + (y) * w)
#define ARRAY_GET_XY(pointer, x, y, w)		(*(pointer + XY(x, y, w)))
#define ARRAY_GET(pointer, i)				(*(pointer + i))

// Dithering
static const uint8_t bayer_metrix_4x4[4][4] = {
	{0, 12,  3, 15},
	{8,  4, 11,  7},
	{2, 14,  1, 13},
	{10, 6,  9,  5}
};

static const uint8_t bayer_metrix_8x8[8][8] = {
	{ 0, 32,  8, 40,  2, 34, 10, 42},
	{48, 16, 56, 24, 50, 18, 58, 26},
	{12, 44,  4, 36, 14, 46,  6, 38},
	{60, 28, 52, 20, 62, 30, 54, 22},
	{ 3, 35, 11, 43,  1, 33,  9, 41},
	{51, 19, 59, 27, 49, 17, 57, 25},
	{15, 47,  7, 39, 13, 45,  5, 37},
	{63, 31, 55, 23, 61, 29, 53, 21}
};

static const uint8_t bayer_metrix_16x16[16][16] = {
	{  0, 128,  32, 160,   8, 136,  40, 168,   2, 130,  34, 162,  10, 138,  42, 170},
	{192,  64, 224,  96, 200,  72, 232, 104, 194,  66, 226,  98, 202,  74, 234, 106},
	{ 48, 176,  16, 144,  56, 184,  24, 152,  50, 178,  18, 146,  58, 186,  26, 154},
	{240, 112, 208,  80, 248, 120, 216,  88, 242, 114, 210,  82, 250, 122, 218,  90},
	{ 12, 140,  44, 172,   4, 132,  36, 164,  14, 142,  46, 174,   6, 134,  38, 166},
	{204,  76, 236, 108, 196,  68, 228, 100, 206,  78, 238, 110, 198,  70, 230, 102},
	{ 60, 188,  28, 156,  52, 180,  20, 148,  62, 190,  30, 158,  54, 182,  22, 150},
	{252, 124, 220,  92, 244, 116, 212,  84, 254, 126, 222,  94, 246, 118, 214,  86},
	{  3, 131,  35, 163,  11, 139,  43, 171,   1, 129,  33, 161,   9, 137,  41, 169},
	{195,  67, 227,  99, 203,  75, 235, 107, 193,  65, 225,  97, 201,  73, 233, 105},
	{ 51, 179,  19, 147,  59, 187,  27, 155,  49, 177,  17, 145,  57, 185,  25, 153},
	{243, 115, 211,  83, 251, 123, 219,  91, 241, 113, 209,  81, 249, 121, 217,  89},
	{ 15, 143,  47, 175,   7, 135,  39, 167,  13, 141,  45, 173,   5, 133,  37, 165},
	{207,  79, 239, 111, 199,  71, 231, 103, 205,  77, 237, 109, 197,  69, 229, 101},
	{ 63, 191,  31, 159,  55, 183,  23, 151,  61, 189,  29, 157,  53, 181,  21, 149},
	{255, 127, 223,  95, 247, 119, 215,  87, 253, 125, 221,  93, 245, 117, 213,  85}
};

int dithering(uint8_t* image, int w, int h, int bayer_size)
{
	uint8_t level_div = 256 / (bayer_size * bayer_size);
	int data_bytes = w * h;
	int N = bayer_size;

	uint8_t* bayer_p;

	// gray level to bayer matrix level
	for (int i = 0; i < data_bytes; i++)
		ARRAY_GET(image, i) /= level_div;

	// chose bayer matrix
	switch (bayer_size)
	{
		case 4:		bayer_p = bayer_metrix_4x4;		break;
		case 8:		bayer_p = bayer_metrix_8x8;		break;
		case 16:	bayer_p = bayer_metrix_16x16;	break;
		default:	return -1;
	}

	// start dither process
	for (int y = 0; y < h; y++)
	{
		for (int x = 0; x < w; x++)
		{
			if (ARRAY_GET_XY(image, x, y, w) > ARRAY_GET_XY(bayer_p, x % N, y % N, N))
			{
				ARRAY_GET_XY(image, x, y, w) = 255;
			}
			else
			{
				ARRAY_GET_XY(image, x, y, w) = 0;
			}
		}
	}

	return 0;
}

// Error diffusion
int error_diffusion(uint8_t* image, int w, int h)
{
	int old_v, new_v, error;
	int data_bytes = w * h;

	int* image_p = malloc(w * h * sizeof(int));

	if (image_p == NULL)
		return -1;

	for (int i = 0; i < data_bytes; i++)
	{
		ARRAY_GET(image_p, i) = (int)ARRAY_GET(image, i);
	}

	for (int y = 0; y < h; y++)
	{
		for (int x = 0; x < w; x++)
		{
			old_v = ARRAY_GET_XY(image_p, x, y, w);
			new_v = (old_v > 127) ? 255 : 0;
			ARRAY_GET_XY(image_p, x, y, w) = new_v;
			error = old_v - new_v;

			if ((0 <= x + 1) && (x + 1 < w) && (0 <= y) && (y < h))
				ARRAY_GET_XY(image_p, x + 1, y, w) += (error * 7 / 16);

			if ((0 <= x + 1) && (x + 1 < w) && (0 <= y + 1) && (y + 1 < h))
				ARRAY_GET_XY(image_p, x + 1, y + 1, w) += (error * 1 / 16);

			if ((0 <= x) && (x < w) && (0 <= y + 1) && (y + 1 < h))
				ARRAY_GET_XY(image_p, x, y + 1, w) += (error * 5 / 16);

			if ((0 <= x - 1) && (x - 1 < w) && (0 <= y + 1) && (y + 1 < h))
				ARRAY_GET_XY(image_p, x - 1, y + 1, w) += (error * 3 / 16);
		}
	}

	for (int i = 0; i < data_bytes; i++)
	{
		ARRAY_GET(image, i) = (uint8_t)ARRAY_GET(image_p, i);
	}

	free(image_p);

	return 0;
}

// Black White image to bytes
int bw2Bytes(uint8_t* image, uint8_t* bytes, int w, int h, bw2bytes_config_t config)
{
	int image_bytes = w * h;
	int out_bytes = image_bytes / 8;
	uint8_t temp;

	// Check if h, w is aligned with byte direction
	if ((config.byte_dir == 0) && (w % 8 != 0))
		return -1;
	if ((config.byte_dir == 1) && (h % 8 != 0))
		return -1;

	// all value to 0 or 1
	for (int i = 0; i < image_bytes; i++)
		ARRAY_GET(image, i) = (ARRAY_GET(image, i) >= 1) ? (uint8_t)1 : (uint8_t)0;

	// horizontal flip
	if (config.flip_h == 1)
	{
		for (int y = 0; y < h; y++)
		{
			for (int x = 0; x < w / 2; x++)
			{
				temp = ARRAY_GET_XY(image, x, y, w);
				ARRAY_GET_XY(image, x, y, w) = ARRAY_GET_XY(image, w - x - 1, y, w);
				ARRAY_GET_XY(image, w - x - 1, y, w) = temp;
			}
		}
	}

	// vertical flip
	if (config.flip_v == 1)
	{
		for (int x = 0; x < w; x++)
		{
			for (int y = 0; y < h / 2; y++)
			{
				temp = ARRAY_GET_XY(image, x, y, w);
				ARRAY_GET_XY(image, x, y, w) = ARRAY_GET_XY(image, x, h - y - 1, w);
				ARRAY_GET_XY(image, x, h - y - 1, w) = temp;
			}
		}
	}

	// scan
	int i = 0;
	// Horizontal Scan
	if (config.scan_dir == 0)
	{
		// byte_dir horizontal
		if (config.byte_dir == 0)
		{
			for (int y = 0; y < h; y++)
			{
				for (int x = 0; x < w; x += 8)
				{
					// sign bit MSB
					if (config.sign_bit == 0)
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x + bits, y, w)) << (7 - bits);
						}
					}
					// sign bit LSB
					else
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x + bits, y, w)) << (bits);
						}
					}

					i++;
				}
			}
		}
		// byte_dir vertical
		else
		{
			for (int y = 0; y < h; y += 8)
			{
				for (int x = 0; x < w; x++)
				{
					// sign bit MSB
					if (config.sign_bit == 0)
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x, y + bits, w)) << (7 - bits);
						}
					}
					// sign bit LSB
					else
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x, y + bits, w)) << (bits);
						}
					}
					
					i++;
				}
			}
		}
	}
	// Vertical Scan
	else
	{
		// byte_dir horizontal
		if (config.byte_dir == 0)
		{
			for (int x = 0; x < w; x += 8)
			{
				for (int y = 0; y < h; y++)
				{
					// sign bit MSB
					if (config.sign_bit == 0)
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x + bits, y, w)) << (7 - bits);
						}
					}
					// sign bit LSB
					else
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x + bits, y, w)) << (bits);
						}
					}

					i++;
				}
			}
		}
		// byte_dir vertical
		else
		{
			for (int x = 0; x < w; x++)
			{
				for (int y = 0; y < h; y += 8)
				{
					// sign bit MSB
					if (config.sign_bit == 0)
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x, y + bits, w)) << (7 - bits);
						}
					}
					// sign bit LSB
					else
					{
						for (int bits = 0; bits < 8; bits++)
						{
							ARRAY_GET(bytes, i) |= (ARRAY_GET_XY(image, x, y + bits, w)) << (bits);
						}
					}

					i++;
				}
			}
		}
	}

	return 0;
}
