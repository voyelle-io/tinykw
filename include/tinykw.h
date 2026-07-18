/**
 * TinyKW - A keyword spotting library
 *
 * Copyright (c) 2026 voyelle-io.
 * 
 * This software is licensed for non-commercial use only.
 * See the LICENSE file in the root of this repository for full terms.
 * 
 * For commercial licensing, contact: https://www.voyelle.io
 *
 * Version: 1.0
 */


#ifndef TKW_PUBLIC_H_
#define TKW_PUBLIC_H_

#ifdef __cplusplus
 extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

#if defined(_WIN32)
  #ifdef TKW_BUILD
    #define TKW_API __declspec(dllexport)
  #else
    #define TKW_API __declspec(dllimport)
  #endif
#elif defined(__arm__) || defined(__thumb__)
  #define TKW_API
#else
  #define TKW_API __attribute__((visibility("default")))
#endif

#define TKW_VERSION_MAJOR 1
#define TKW_VERSION_MINOR 0
#define TKW_VERSION_PATCH 0

#define TKW_AUDIO_FRAME_SIZE (480)

typedef enum {
    TKW_OK = 0,
    TKW_NOT_INITIALIZED = 1,
    TKW_TOO_MANY_KEYWORDS = 2,
    TKW_INVALID_KEYWORD_BYTES = 3,
    TKW_WRONG_INPUT_SIZE = 4,
    TKW_INVALID_ARGUMENT = 5,
    TKW_INVALID_KEYWORD_ID = 6,
    TKW_INTERNAL_ERROR = 7,
} tkw_status;


/*
 * Initialize the TKW engine.
 * This should be called before any other API function.
 * Calling tkw_init() multiple times is allowed and resets all internal state,
 * including registered keywords and detection flags.
 */
TKW_API tkw_status tkw_init(void);

/* 
 * Adds a keyword to be detected.
 *
 * Inputs:
 *  - data: pointer to the 48-byte encoded keyword (can be obtained from https://www.voyelle.io/tinykw)
 *  - detection_threshold: value in q7 between 0 and 255. Controls how strict the engine is when deciding whether a detection is valid.
 *      * A high value makes the engine more conservative: only high-scoring detections are accepted (fewer false positives, but more missed detections).
 *      * A low value makes the engine more permissive: more detections are accepted (fewer misses, but more false positives).
 *      * This parameter may need tuning depending on the keyword, use case and environment. A good starting point is to set it mid-range at 128, and 
 *        then eventually adjust based on your tolerance for false positives vs missed detections.
 *  - out_id: receives the assigned keyword ID
 */
TKW_API tkw_status tkw_add_keyword(const uint8_t data[48], uint8_t detection_threshold, uint32_t* out_id);

/*
 * Processes one frame of 16-bit PCM audio sampled at 16 kHz.
 *
 * Inputs:
 *  - waveform: pointer to audio samples
 *  - size: number of samples in waveform, must equal TKW_AUDIO_FRAME_SIZE
 */
TKW_API tkw_status tkw_process_frame(const int16_t* waveform, size_t size);

/*
 * Reads the detection flag for a specific keyword.
 *
 * On success, writes:
 *  - 1 if detected
 *  - 0 otherwise
 *
 * Detection remains set until cleared with tkw_clear_keyword_flag().
 */
TKW_API tkw_status tkw_is_keyword_detected(uint32_t keyword_id, uint32_t* out_detected);

/*
 * Clears the detection flag for a specific keyword.
 */
TKW_API tkw_status tkw_clear_keyword_flag(uint32_t keyword_id);


/*
 * Returns a human-readable string for a status code.
 * The returned pointer refers to a static string and must not be freed.
 */
TKW_API const char* tkw_status_string(tkw_status status);


#ifdef __cplusplus
}
#endif

#endif
