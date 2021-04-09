#include <stdio.h>
#include <stdlib.h>

using namespace std;

int main() {
	char cmd[128];	
	sprintf(cmd,"clang++ -std=c++11 -lclang ngetapi.cpp -o ngetapi");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11 -lclang ngetpoint.cpp -o ngetpoint");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11 -lclang ngetarr.cpp -o ngetarr");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11 -lclang ngetbds.cpp -o ngetbds");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11 -lclang ngetval.cpp -o ngetval");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11  nslicerline.cpp -o nslicerline");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11  nslicerlinemuti.cpp -o nslicerlinemuti");
	system(cmd);
	sprintf(cmd,"clang++ -std=c++11  get-llvmwithline.cpp -o get-llvmwithline");
	system(cmd);
	return 0;
}
