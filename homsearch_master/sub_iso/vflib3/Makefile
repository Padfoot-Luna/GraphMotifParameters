CXXFLAGS= -std=c++11 -O3 -Wall -Wno-deprecated -Iinclude
# Default target:
all: vf3 #vf3k


.PHONY: all vf3 #vf3k
vf3: bin/vf3
# vf3k: bin/vf3k

bin/vf3: src/main.cpp $(ls include)
	$(CXX) $(CXXFLAGS) -o $@ $< 

# bin/vf3k: src/main.cpp $(ls include)
# 	$(CXX) $(CXXFLAGS) -DVF3K=4 -o $@ $<
	
.PHONY: doc
doc:
	doxygen ./doc/doxygen.conf

.PHONY: test
test: bin/vf3 #bin/vf3k
	@bin/vf3 test/bvg1.sub.grf test/bvg1.grf
	#@bin/vf3k test/bvg1.sub.grf test/bvg1.grf

.PHONY: clean
clean:
	rm ./bin/*
	rm -rf ./doc/html
	rm -rf ./doc/latex