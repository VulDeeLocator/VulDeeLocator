#include <iostream>
#include <fstream>
#include <stdio.h>
#include <string.h>
#include <string>
#include <algorithm>
#include <stdlib.h>
#include <vector>
#include <sstream>

using namespace std;

int main(int argc, char *argv[])
{
	char cmd[2000];
	vector<string> va,filenofind;
	ifstream in(argv[1]);
	for(string ss;in>>ss;)
		va.push_back(ss);
	for(int i=0,j=0,k=1;i<va.size()/2;i++,j=j+2,k=k+2)
	{
		string txt = va[j];
		fstream _file;
     		_file.open(txt.c_str(), ios::in);
     		if(!_file)
	     	{
			filenofind.push_back(txt);
	    	}
     		else
     		{
			string dir;
			int index=txt.size();
			while(txt[index-1]!='/')
			{
			   index--;
			}
			dir=(txt.substr(0,index-1));

			sprintf(cmd,"./ngetpoint %s >data-point.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./nslicerline %s data-point.txt %s",txt.c_str(),va[k].c_str());
			system(cmd);
			sprintf(cmd,"mkdir -p %s/point",dir.c_str());
			system(cmd);
			sprintf(cmd,"mv data-point.txt %s/*.ll %s/point",dir.c_str(),dir.c_str());
			system(cmd);

			cout << "point over"<< endl;

			sprintf(cmd,"./ngetarr %s >data-arr.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./nslicerline %s data-arr.txt %s",txt.c_str(),va[k].c_str());
			system(cmd);
			sprintf(cmd,"mkdir -p %s/arr",dir.c_str());
			system(cmd);
			sprintf(cmd,"mv data-arr.txt %s/*.ll %s/arr",dir.c_str(),dir.c_str());
			system(cmd);

			cout << "arr over"<< endl;

			sprintf(cmd,"./ngetbds %s >data-bds.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./ngetval %s >data-val.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./nslicerlinemuti %s data-bds.txt %s data-val.txt",txt.c_str(),va[k].c_str());
			system(cmd);
			sprintf(cmd,"mkdir -p %s/bds",dir.c_str());
			system(cmd);
			sprintf(cmd,"mv data-bds.txt data-val.txt %s/*.ll %s/bds",dir.c_str(),dir.c_str());
			system(cmd);

			cout << "bds over"<< endl;

			sprintf(cmd,"./ngetapi %s >data-api.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./ngetval %s >data-val.txt",txt.c_str());
			system(cmd);
			sprintf(cmd,"./nslicerlinemuti %s data-api.txt %s data-val.txt",txt.c_str(),va[k].c_str());
			system(cmd);
			sprintf(cmd,"mkdir -p %s/api",dir.c_str());
			system(cmd);
			sprintf(cmd,"mv data-api.txt data-val.txt %s/*.ll %s/api",dir.c_str(),dir.c_str());
			system(cmd);

			cout << "api over"<< endl;
		}
	}
}
