BUILD_DIR := build

TINYKW_INCLUDE_DIR := ../../include
# Path to be modified according to platform
TINYKW_LIB_PATH := ../../libs/macos-x86_64/en/
TINYKW_LIB_NAME := tinykw

SRCS := microphone_portaudio.c
BINS := $(SRCS:%.c=$(BUILD_DIR)/%.bin)

CC := gcc
INCLUDE_DIRS := -I$(TINYKW_INCLUDE_DIR) -I/usr/local/include
LIBRARY_PATHS := -L$(TINYKW_LIB_PATH) -L/usr/local/lib
LIBRARY_NAMES := -l$(TINYKW_LIB_NAME) -lportaudio

.PHONY: all
all: $(BINS)

$(BUILD_DIR)/%.bin: %.c
	mkdir -p $(dir $@)
	$(CC) -o $@ $< $(INCLUDE_DIRS) $(LIBRARY_PATHS) $(LIBRARY_NAMES)

.PHONY: clean
clean: 
	rm -rf $(BUILD_DIR)