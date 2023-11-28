# Copyright (c) 2020-present Caps Collective & contributors
# Originally authored by Jonathan Moallem (@jonjondev) & Aryeh Zinn (@Raelr)
#
# This code is released under an unmodified zlib license.
# For conditions of distribution and use, please see:
#     https://opensource.org/licenses/Zlib

# Define custom functions
rwildcard = $(wildcard $1$2) $(foreach d,$(wildcard $1*),$(call rwildcard,$d/,$2))
platformpth = $(subst /,$(PATHSEP),$1)
fixraylib = $(FIXSCRIPT)
createBuildDir = $(BINSCRIPT)

# Set global macros
buildDir := bin
executable := app
target := $(buildDir)/$(executable)
sources := $(call rwildcard,src/,*.cpp) $(call rwildcard,include/,*.cpp)
objects := $(patsubst src/%, $(buildDir)/%, $(patsubst %.cpp, %.o, $(sources)))
depends := $(patsubst %.o, %.d, $(objects))
compileFlags := -std=c++17 -I include include/raygui-cpp include/extras
linkFlags = -L lib/$(platform) -l raylib 

# Check for Windows
ifeq ($(OS), Windows_NT)
	# Set Windows macros
	platform := Windows
	CXX ?= g++
	linkFlags += -Wl,--allow-multiple-definition -pthread -lopengl32 -lgdi32 -lwinmm -static -static-libgcc -static-libstdc++
	THEN := &&
	PATHSEP := \$(BLANK)
	MKDIR := -mkdir
	RM := -del /q
	COPY = -robocopy "$(call platformpth,$1)" "$(call platformpth,$2)" $3
	FIXSCRIPT := powershell -File scripts/raylib-fix.ps1
	BINSCRIPT := powershell -File scripts/setup-file-tree.ps1
else
	# Check for MacOS/Linux
	UNAMEOS := $(shell uname)
	ifeq ($(UNAMEOS), Linux)
		# Set Linux macros
		platform := Linux
		CXX ?= g++
		linkFlags += -l GL -l m -l pthread -l dl -l rt -l X11
	endif
	ifeq ($(UNAMEOS), Darwin)
		# Set macOS macros
		platform := macOS
		CXX ?= clang++
		linkFlags += -framework CoreVideo -framework IOKit -framework Cocoa -framework GLUT -framework OpenGL
	endif

	# Set UNIX macros
	THEN := ;
	PATHSEP := /
	MKDIR := mkdir -p
	RM := rm -rf
	COPY = cp $1$(PATHSEP)$3 $2
	FIXSCRIPT := ./scripts/raylib-fix.sh
	BINSCRIPT := ./scripts/setup-file-tree.sh
endif

# Lists phony targets for Makefile
.PHONY: all setup submodules execute clean

# Default target, compiles, executes and cleans
all: bin_setup $(target) execute clean

bin_setup:
	$(call createBuildDir)

# Sets up the project for compiling, generates includes and libs
setup: include lib bin_setup

# Pull and update the the build submodules
submodules:
	git submodule update --init --recursive --depth 1
#	$(call fixraylib)

# Copy the relevant header files into includes
include: submodules
	$(MKDIR) $(call platformpth, ./include)
#	$(MKDIR) $(call platformpth, ./include/src)
	$(MKDIR) $(call platformpth, include/raygui-cpp)
	$(MKDIR) $(call platformpth, include/extras)

	$(call COPY,vendor/raylib/src,./include,raylib.h)
	$(call COPY,vendor/raylib/src,./include,raymath.h)
	$(call COPY,vendor/raylib/src,./include,rlgl.h)

	$(call COPY,vendor/raylib-cpp/include,./include,*.hpp)
	$(call COPY,vendor/raygui-cpp/include,./include,raygui-cpp.h)

	$(call COPY,vendor/raygui-cpp/dependencies/raylib/src,./include,raygui.h)
	$(call COPY,vendor/raygui-cpp/include/raygui-cpp,./include/raygui-cpp,*.h)

	$(call COPY,vendor/imgui,./include,*.h)
	$(call COPY,vendor/imgui,./include,*.cpp)
#	$(call COPY,vendor/imgui,./include/src,*.cpp)

	$(call COPY,vendor/rlImGui,./include,*.h)
	$(call COPY,vendor/rlImGui,./include,*.cpp)
#	$(call COPY,vendor/rlImGui,./include/src,*.cpp)
	$(call COPY,vendor/rlImGui/extras,./include/extras,*.h)

# Build the raylib static library file and copy it into lib
lib: submodules
	cd vendor/raylib/src $(THEN) "$(MAKE)" PLATFORM=PLATFORM_DESKTOP
	$(MKDIR) $(call platformpth, lib/$(platform))
	$(call COPY,vendor/raylib/src,lib/$(platform),libraylib.a)

test_fixraylib:
	$(call fixraylib)

# Link the program and create the executable
$(target): $(objects)
	$(CXX) $(objects) -o $(target) $(linkFlags)

# Add all rules from dependency files
-include $(depends)

# Compile objects to the build directory
$(buildDir)/%.o: src/%.cpp Makefile
	$(MKDIR) $(call platformpth, $(@D))
	$(CXX) -MMD -MP -c $(compileFlags) $< -o $@ $(CXXFLAGS)

# Run the executable
execute:
	$(target) $(ARGS)

# Clean up all relevant files
clean:
	rm -rf $(buildDir)/*
