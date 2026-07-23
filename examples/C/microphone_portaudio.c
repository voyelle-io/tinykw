/*
This demo uses Portaudio (https://portaudio.com/) to read the microphone audio and TinyKW to detect keywords.
*/
#include <string.h>
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>
#include <signal.h>
#include <assert.h>

#include "portaudio.h"
#include "tinykw.h"

#define SAMPLE_RATE (16000)
#define NUM_SECONDS (180)
#define NB_KEYWORDS (4)

static volatile int keepRunning = 1;

void intHandler(int dummy) {
    keepRunning = 0;
}

int microphone_demo()
{
    signal(SIGINT, intHandler);
    tkw_status status;

    /* Creates and Initializes TinyKW context */
    tkw_context ctx;
    status = tkw_init(&ctx);
    assert(status == TKW_OK);
    printf("TinyKW engine initialized.\n");

    /* For printing purposes. */
    char* keyword_names[] = {"hello world", "banana split", "superstar", "a cup of coffee"};
    
    /* Encoding of keywords can be retrieved from https://voyelle.io/tinykw. */
    const uint8_t keyword_bytes[NB_KEYWORDS][48] = {
        {0x11, 0xb4, 0x15, 0xc0, 0x54, 0xb6, 0xcc, 0x22, 0xc5, 0xb6, 0xd6, 0x2e, 0x7a, 0xe3, 0xb9, 0x75, 0xf6, 0xb6, 0xbc, 0x70, 0xf7, 0x29, 0x3b, 0x14, 0x67, 0x9a, 0x81, 0x07, 0x93, 0x51, 0xa2, 0x90, 0x40, 0x74, 0xc9, 0x06, 0xb6, 0x41, 0x6a, 0xf5, 0x2a, 0xe2, 0x7c, 0x39, 0xfa, 0x9e, 0x5a, 0x92},
	    {0x58, 0xef, 0x25, 0x32, 0x4b, 0x18, 0x95, 0x67, 0x20, 0x52, 0x85, 0x4b, 0x34, 0x02, 0x7b, 0x9e, 0x6b, 0x61, 0x8a, 0x17, 0xf9, 0x6f, 0x8c, 0xfd, 0x8a, 0x7f, 0x2b, 0x1f, 0x49, 0x5b, 0x46, 0x81, 0xed, 0x3e, 0xdf, 0xc1, 0x5a, 0x98, 0x40, 0x9c, 0xd0, 0x59, 0xed, 0xdd, 0x6e, 0x3a, 0xa2, 0x56},
	    {0x51, 0x49, 0x06, 0xc3, 0x9a, 0x61, 0xcc, 0x9c, 0x4d, 0x2c, 0x75, 0x51, 0x80, 0xa4, 0xb2, 0xc7, 0xc2, 0xd5, 0x70, 0x72, 0xdc, 0x8a, 0xc7, 0x8e, 0x36, 0x55, 0x61, 0xd1, 0x56, 0x92, 0x6e, 0xad, 0xcb, 0xec, 0x0c, 0x4d, 0xd4, 0x05, 0x86, 0xb1, 0x25, 0xad, 0x7a, 0xd7, 0xd4, 0xdc, 0x98, 0x90},
	    {0xec, 0x87, 0x37, 0x7c, 0x70, 0x8f, 0x44, 0x14, 0x89, 0x1f, 0x10, 0xe0, 0x55, 0xd4, 0x7e, 0xb4, 0xcc, 0x86, 0x7e, 0x69, 0x47, 0xad, 0x77, 0xad, 0x9a, 0x05, 0xc1, 0x04, 0x30, 0x83, 0xae, 0x16, 0x2b, 0xd8, 0xd1, 0x9a, 0x90, 0x6a, 0x7f, 0x03, 0x49, 0x3d, 0x05, 0x96, 0x84, 0x8a, 0x52, 0x2a}    
    };

    /* Add the keywords to the engine */
    uint32_t keyword_ids[NB_KEYWORDS];
    for (int k = 0; k < NB_KEYWORDS; ++k)
    {
        status = tkw_add_keyword(keyword_bytes[k], 128, &(keyword_ids[k]), &ctx);
        assert(status == TKW_OK);
    }
    printf("Keywords added.\n");

    /* Read and process microphone's data using Portaudio */
    PaStream *stream;
    PaError err;
    PaStreamParameters inputParameters;
    err = Pa_Initialize();
    if( err != paNoError ) goto done;

    //inputParameters.device = 1;
    inputParameters.device = Pa_GetDefaultInputDevice();
    if (inputParameters.device == paNoDevice) {
        fprintf(stderr,"Error: No default input device.\n");
        goto done;
    }
    inputParameters.channelCount = 1;
    inputParameters.sampleFormat = paInt16;
    inputParameters.suggestedLatency = Pa_GetDeviceInfo( inputParameters.device )->defaultLowInputLatency;
    inputParameters.hostApiSpecificStreamInfo = NULL;

    err = Pa_OpenStream(
              &stream,
              &inputParameters,
              NULL,
              SAMPLE_RATE,
              TKW_AUDIO_FRAME_SIZE,
              paClipOff,
              NULL,
              NULL );
    if( err != paNoError ) goto done;
    
    err = Pa_StartStream( stream );
    if( err != paNoError ) goto done;
    printf("Wire on. Will run %d seconds.\n", NUM_SECONDS); fflush(stdout);

    int16_t sampleBlock[TKW_AUDIO_FRAME_SIZE];
    float avg = 0;
    for (int k = 0; k < NUM_SECONDS * SAMPLE_RATE / TKW_AUDIO_FRAME_SIZE; ++k)
    {
        err = Pa_ReadStream( stream, sampleBlock, TKW_AUDIO_FRAME_SIZE );
        if( err ) goto xrun;
            status = tkw_process_frame(sampleBlock, TKW_AUDIO_FRAME_SIZE, &ctx); // process one frame
            assert(status == TKW_OK);
            for (int i = 0; i < NB_KEYWORDS; ++i)
            {
                uint32_t is_detected = 0;
                status = tkw_is_keyword_detected(keyword_ids[i], &is_detected, &ctx); // check detection
                assert(status == TKW_OK);
                if (is_detected)
                {
                    status = tkw_clear_keyword_flag(i, &ctx); // clear flag
                    assert(status == TKW_OK);
                    printf("%s detected\n", keyword_names[i]); fflush(stdout);
                }
            }

        if (keepRunning == 0)
            break;
    }
    printf("Wire off.\n"); fflush(stdout);

    // stop stream
    err = Pa_StopStream( stream );
    if( err != paNoError ) goto done;

    Pa_Terminate();
    return 0;

    xrun:
        printf("err = %d\n", err); fflush(stdout);
        if( stream ) {
            Pa_AbortStream( stream );
            Pa_CloseStream( stream );
        }
        Pa_Terminate();
        if( err & paInputOverflow )
            fprintf( stderr, "Input Overflow.\n" );
        if( err & paOutputUnderflow )
            fprintf( stderr, "Output Underflow.\n" );
        return -2;

    done:
        Pa_Terminate();
        if( err != paNoError )
        {
            fprintf( stderr, "An error occurred while using the portaudio stream\n" );
            fprintf( stderr, "Error number: %d\n", err );
            fprintf( stderr, "Error message: %s\n", Pa_GetErrorText( err ) );
            err = 1;          /* Always return 0 or 1, but no other return codes. */
        }
        return err;
}

int main(int argc, char *argv[])
{
    printf("MICROPHONE EXAMPLE\n");
    microphone_demo();
}
