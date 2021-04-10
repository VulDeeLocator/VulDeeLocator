#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>

using namespace std;

int main(int argc, char *argv[])
{
	char cmd[2000];
	vector<string> va;
	string path = argv[1];

	ifstream in(path.c_str());
	for(string ss;in>>ss;)
		va.push_back(ss);
			
	string txt = va[0];
	string dir;

	int index=txt.size();
	while(txt[index-1]!='/')
	{
		index--;
	}
	dir=(txt.substr(0,index-1));

	sprintf(cmd,"./ngetpoint %s >data-point.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./nslicerline %s data-point.txt",path.c_str());
	system(cmd);
	sprintf(cmd,"mkdir -p %s/point",dir.c_str());
	system(cmd);
	sprintf(cmd,"mv data-point.txt *.ll %s/point",dir.c_str());
	system(cmd);
			
	cout << "point over"<< endl;

	sprintf(cmd,"./ngetarr %s >data-arr.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./nslicerline %s data-arr.txt",path.c_str());
	system(cmd);
	sprintf(cmd,"mkdir -p %s/arr",dir.c_str());
	system(cmd);
	sprintf(cmd,"mv data-arr.txt *.ll %s/arr",dir.c_str());
	system(cmd);
			
	cout << "arr over"<< endl;

	sprintf(cmd,"./ngetbds %s >data-bds.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./ngetval %s >data-val.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./nslicerlinemuti %s data-bds.txt data-val.txt",path.c_str());
	system(cmd);
	sprintf(cmd,"mkdir -p %s/bds",dir.c_str());
	system(cmd);
	sprintf(cmd,"mv data-bds.txt data-val.txt *.ll %s/bds",dir.c_str());
	system(cmd);

	cout << "bds over"<< endl;

	sprintf(cmd,"./ngetapi %s >data-api.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./ngetval %s >data-val.txt",txt.c_str());
	system(cmd);
	sprintf(cmd,"./nslicerlinemuti %s data-api.txt data-val.txt",path.c_str());
	system(cmd);
	sprintf(cmd,"mkdir -p %s/api",dir.c_str());
	system(cmd);
	sprintf(cmd,"mv data-api.txt data-val.txt *.ll %s/api",dir.c_str());
	system(cmd);

	cout << "api over"<< endl;
}
