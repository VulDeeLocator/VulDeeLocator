#include  <iostream>
#include  <string>
#include  <cstring>
#include  <map>
#include  <vector>
#include  <algorithm>
#include "clang-c/Index.h"

using namespace std;

map<string,string>typmap;

int countstr(string sstr,char son) {
	const char *str = sstr.c_str();
	int idx = 0;
	int num = 0;
	while(str[idx]!='\0') {
		if(str[idx]==son)	num++;
		idx++;
	}
	return num;
}

string subspace(string father){
        const char *fch = father.c_str();
        int len = father.length();
        if(fch[len-1]=='*'){
                string son = father.substr(0,len-2);
                return son;
        }
        return father;
}

int isContent(string father,string son) {
	const char *fch = father.c_str();
	const char *sch = son.c_str();
	int tag = 0;
	int i = tag;
	int j = 0;
	while(fch[i]!='\0'&&sch[j]!='\0') {
		if(fch[i]==sch[j]) {
			i++;
			j++;
		} else {
			tag++;
			i = tag;
			j=0;
		}
	}
	if(sch[j] == '\0')
		return 1;
	else
		return 0;
}

string getCursorSpelling( CXCursor cursor ){
        CXString cursorSpelling = clang_getCursorSpelling(cursor);
        string result      = clang_getCString( cursorSpelling );
        clang_disposeString( cursorSpelling );
        return result;
}

string getTypeSpelling( CXCursor cursor ){
        CXType ctp=clang_getCursorType(cursor);
        CXString cursorSpelling = clang_getTypeSpelling(ctp);
        string result      = clang_getCString( cursorSpelling );
        clang_disposeString( cursorSpelling );
        int starnum = countstr(result,'*');
        map<string, string>::iterator iter;
        result = subspace(result);
        iter = typmap.find(result);
        if(iter != typmap.end()) { 
                result = iter->second;
        }
        while(starnum>0){
                result = result+'*';
                starnum--;
        }
        return result;
}
string getCursorSpelling1( CXCursor cursor ){
        CXString cursorSpelling = clang_getCursorDisplayName( cursor );
        string result      = clang_getCString( cursorSpelling );
        clang_disposeString( cursorSpelling );
        return result;
}

string getCursorSpelling4( CXCursor cursor ){
        CXCursorKind cursor1=clang_getCursorKind (cursor);
        CXString c2=clang_getCursorKindSpelling (cursor1);
        string result      = clang_getCString( c2 );
        clang_disposeString( c2);
        return result;
}
void getCursorSpelling2( CXCursor cursor ){
        CXSourceRange range = clang_getCursorExtent(cursor);
        CXSourceLocation location = clang_getRangeStart(range);
        CXSourceLocation location1 = clang_getRangeEnd(range);
        CXFile file;
        unsigned line,line1,offset;
        unsigned column,column1;
        clang_getFileLocation(location, &file, &line, &column, &offset);
        clang_getFileLocation(location1, &file, &line1, &column1, nullptr);
        auto fileName = clang_getFileName(file);
        CXFileUniqueID outID;
        clang_getFileUniqueID (file, &outID);
        CXTranslationUnit TU= clang_Cursor_getTranslationUnit (cursor);
        CXTUResourceUsage  TUS=clang_getCXTUResourceUsage (TU);
        cout<<line1 <<  " "; 
}

CXChildVisitResult functionVisitor(CXCursor cursor, CXCursor parent, CXClientData clientData){
        CXSourceLocation location = clang_getCursorLocation( cursor );
        CXFile file;
        unsigned int line;
        unsigned int column;
        unsigned int offset;
        clang_getFileLocation(location, &file, &line, &column, &offset);
        if( clang_Location_isFromMainFile( location ) == 0){
                return CXChildVisit_Continue;
        }
        vector<string> apilist  = *( reinterpret_cast<vector<string>*>( clientData ) );
        CXCursorKind kind = clang_getCursorKind( cursor );
        CXCursorKind kindparent = clang_getCursorKind( parent );
        string apispelling=getCursorSpelling1( cursor );
        int nRet=0;
        for (int i = 0; i < apilist.size(); ++i)
        {	
                        int start =apilist[i].find_first_of("*");
                        int end =apilist[i].find_last_of("*");
                        int num=count(apilist[i].begin(),apilist[i].end(),'*');
                        if(num!=0)
                        {
                                if(num==1&&start==0)
                                {
                                        int N=apispelling.find_first_of("alloc");
                                        if(N!=0&&apispelling[apispelling.size()-1]=='c') nRet=1;	
                                }

                                if(num==1&&start!=0)
                                {
                                        string str =apilist[i];
                                        str.erase(remove(str.begin(), str.end(), '*'), str.end());
                                        int N=apispelling.find(str);
                                        if(N==0)nRet=1;
                                } 
                                if(num==2)
                                {
                                        string str =apilist[i];
                                        str.erase(remove(str.begin(), str.end(), '*'), str.end());
                                        int N=apispelling.find(str);
                                        if(N!=-1)nRet=1;
                                }
                        }
                        else if (apilist[i]==apispelling)
                        {
                                nRet=1;
                        }
        }
        if((kind == CXCursorKind::CXCursor_DeclRefExpr&&!nRet&&kindparent!=CXCursorKind::CXCursor_MemberRefExpr)||kind== CXCursorKind::CXCursor_MemberRefExpr)
        {
                CXTranslationUnit tu = clang_Cursor_getTranslationUnit(cursor);
                CXSourceRange range = clang_getCursorExtent(cursor);
                CXToken* tokens;
                unsigned int numTokens;
                clang_tokenize(tu, range, &tokens, &numTokens);
                if(kind== CXCursorKind::CXCursor_DeclRefExpr){
                        string spelling2 = getTypeSpelling( cursor );
                        string key1="[";string key2="*";
                        string::size_type idx1,idx2;
                        idx1=spelling2.find(key1);idx2=spelling2.find(key2);
                        int pnum = countstr(spelling2,'*');
                        if (idx1!=string::npos||idx2!=string::npos)   
                        { 
                                                if(!isContent(spelling2,"struct")&&!isContent(spelling2,"void")
                                                &&!isContent(spelling2,"FILE"))
                                                
                                                while(pnum!=0) {
                                                        pnum--;
                                                }
                        }
                string spelling = getCursorSpelling( cursor );
                cout<<spelling<<" ";    }        //getCursorSpelling	
                return CXChildVisit_Recurse;
        }
        return CXChildVisit_Recurse;
}

CXChildVisitResult findchild(CXCursor cursor, CXCursor parent, CXClientData clientData){
        CXSourceLocation location = clang_getCursorLocation( cursor );
                CXFile file;
                unsigned int line;
                unsigned int column;
                unsigned int offset;
                clang_getFileLocation(location, &file, &line, &column, &offset);
                if( clang_Location_isFromMainFile( location ) == 0){
                return CXChildVisit_Continue;
        }
        vector<string> apilist  = *( reinterpret_cast<vector<string>*>( clientData ) );
        CXCursorKind kind = clang_getCursorKind( cursor );
        string apispelling=getCursorSpelling1( cursor );
        string spelling5 = getCursorSpelling4( parent );
        string spelling = getCursorSpelling(cursor);
        int nRet=0;
        for (int i = 0; i < apilist.size(); ++i)
        {	
                        int start =apilist[i].find_first_of("*");
                        int end =apilist[i].find_last_of("*");
                        int num=count(apilist[i].begin(),apilist[i].end(),'*');
                        if(num!=0)
                        {
                                if(num==1&&start==0)
                                {
                                        int N=apispelling.find_first_of("alloc");
                                        if(N!=0&&apispelling[apispelling.size()-1]=='c') nRet=1;	
                                }

                                if(num==1&&start!=0)
                                {
                                        string str =apilist[i];
                                        str.erase(remove(str.begin(), str.end(), '*'), str.end());
                                        int N=apispelling.find(str);
                                        if(N==0)nRet=1;
                                } 
                                if(num==2)
                                {
                                        string str =apilist[i];
                                        str.erase(remove(str.begin(), str.end(), '*'), str.end());
                                        int N=apispelling.find(str);
                                        if(N!=-1)nRet=1;
                                }
                        }
                        else if (apilist[i]==apispelling)
                        {
                                nRet=1;
                        }
        }
        if (kind==CXCursorKind::CXCursor_FunctionDecl)   
        { 
                cout<<spelling<<endl;
        }
        if(kind == CXCursorKind::CXCursor_CallExpr&&nRet&&spelling5!="BinaryOperator")
        {
                CXTranslationUnit tu = clang_Cursor_getTranslationUnit(cursor);
                CXSourceRange range = clang_getCursorExtent(cursor);
                CXToken* tokens;
                unsigned int numTokens;
                clang_tokenize(tu, range, &tokens, &numTokens);
                getCursorSpelling2(cursor);
                clang_visitChildren( cursor, functionVisitor, &apilist );   
                cout<<endl;
                return CXChildVisit_Recurse;
        }
        return CXChildVisit_Recurse;
}

CXChildVisitResult setMap(CXCursor cursor, CXCursor parent, CXClientData clientData) {
        CXSourceLocation location = clang_getCursorLocation( cursor );
        CXFile file;
        unsigned int line,line1;
        unsigned int column,column1;
        unsigned int offset;
        clang_getFileLocation(location, &file, &line, &column, &offset);
        if( clang_Location_isFromMainFile( location ) == 0) {
                return CXChildVisit_Continue;
        }


        CXType defctp = clang_getTypedefDeclUnderlyingType(cursor);
        CXString defcursorspelling = clang_getTypeSpelling(defctp);
        string defname = clang_getCString(defcursorspelling);   
        clang_disposeString(defcursorspelling);

        CXType ctp=clang_getCursorType(cursor);
        CXString cursorSpelling = clang_getTypeSpelling(ctp);
        string result = clang_getCString( cursorSpelling );     
        clang_disposeString( cursorSpelling );

        if(defname != "" && result!="") { 
                map<string, string>::iterator iter;
                iter = typmap.find(result);
                if(iter == typmap.end()) { 
                        typmap.insert(map<string, string>::value_type (result,defname));
                }
        }

        return CXChildVisit_Recurse;

}
int main(int argc, char** argv){
        CXIndex index = clang_createIndex(0, 0);
        constexpr const char *ARGUMENTS[] = {};
        CXTranslationUnit  unit = clang_parseTranslationUnit(
                index, 
                argv[1], 
                ARGUMENTS, 
                extent<decltype(ARGUMENTS)>::value,
                nullptr, 
                0, 
                CXTranslationUnit_None
        );


        if(unit == nullptr){
                printf("Unable to parse given file\n");
        }
        else{
                CXCursor cursor = clang_getTranslationUnitCursor( unit );
                clang_visitChildren( cursor, setMap, nullptr );
                vector<string> apilist;
                apilist={"StrNCat", "getaddrinfo", "_ui64toa", "fclose", "pthread_mutex_lock", "gets_s", "sleep", "_ui64tot", "freopen_s", "_ui64tow", "send", "lstrcat", "HMAC_Update", "__fxstat", "StrCatBuff", "_mbscat", "_mbstok_s", "_cprintf_s", "ldap_search_init_page", "memmove_s", "ctime_s", "vswprintf", "vswprintf_s", "_snwprintf", "_gmtime_s", "_tccpy", "*RC6*", "_mbslwr_s", "random", "__wcstof_internal", "_wcslwr_s", "_ctime32_s", "wcsncat*", "MD5_Init", "_ultoa", "snprintf", "memset", "syslog", "_vsnprintf_s", "HeapAlloc", "pthread_mutex_destroy", "ChangeWindowMessageFilter", "_ultot", "crypt_r", "_strupr_s_l", "LoadLibraryExA", "_strerror_s", "LoadLibraryExW", "wvsprintf", "MoveFileEx", "_strdate_s", "SHA1", "sprintfW", "StrCatNW", "_scanf_s_l", "pthread_attr_init", "_wtmpnam_s", "snscanf", "_sprintf_s_l", "dlopen", "sprintfA", "timed_mutex", "OemToCharA", "ldap_delete_ext", "sethostid", "popen", "OemToCharW", "_gettws", "vfork", "_wcsnset_s_l", "sendmsg", "_mbsncat", "wvnsprintfA", "HeapFree", "_wcserror_s", "realloc", "_snprintf*", "wcstok", "_strncat*", "StrNCpy", "_wasctime_s", "push*", "_lfind_s", "CC_SHA512", "ldap_compare_ext_s", "wcscat_s", "strdup", "_chsize_s", "sprintf_s", "CC_MD4_Init", "wcsncpy", "_wfreopen_s", "_wcsupr_s", "_searchenv_s", "ldap_modify_ext_s", "_wsplitpath", "CC_SHA384_Final", "MD2", "RtlCopyMemory", "lstrcatW", "MD4", "MD5", "_wcstok_s_l", "_vsnwprintf_s", "ldap_modify_s", "strerror", "_lsearch_s", "_mbsnbcat_s", "_wsplitpath_s", "MD4_Update", "_mbccpy_s", "_strncpy_s_l", "_snprintf_s", "CC_SHA512_Init", "fwscanf_s", "_snwprintf_s", "CC_SHA1", "swprintf", "fprintf", "EVP_DigestInit_ex", "strlen", "SHA1_Init", "strncat", "_getws_s", "CC_MD4_Final", "wnsprintfW", "lcong48", "lrand48", "write", "HMAC_Init", "_wfopen_s", "wmemchr", "_tmakepath", "wnsprintfA", "lstrcpynW", "scanf_s", "_mbsncpy_s_l", "_localtime64_s", "fstream.open", "_wmakepath", "Connection.open", "_tccat", "valloc", "setgroups", "unlink", "fstream.put", "wsprintfA", "*SHA1*", "_wsearchenv_s", "ualstrcpyA", "CC_MD5_Update", "strerror_s", "HeapCreate", "ualstrcpyW", "__xstat", "_wmktemp_s", "StrCatChainW", "ldap_search_st", "_mbstowcs_s_l", "ldap_modify_ext", "_mbsset_s", "strncpy_s", "move", "execle", "StrCat", "xrealloc", "wcsncpy_s", "_tcsncpy*", "execlp", "RIPEMD160_Final", "ldap_search_s", "EnterCriticalSection", "_wctomb_s_l", "fwrite", "_gmtime64_s", "sscanf_s", "wcscat", "_strupr_s", "wcrtomb_s", "VirtualLock", "ldap_add_ext_s", "_mbscpy", "_localtime32_s", "lstrcpy", "_wcsncpy*", "CC_SHA1_Init", "_getts", "_wfopen", "__xstat64", "strcoll", "_fwscanf_s_l", "_mbslwr_s_l", "RegOpenKey", "makepath", "seed48", "CC_SHA256", "sendto", "execv", "CalculateDigest", "memchr", "_mbscpy_s", "_strtime_s", "ldap_search_ext_s", "_chmod", "flock", "__fxstat64", "_vsntprintf", "CC_SHA256_Init", "_itoa_s", "__wcserror_s", "_gcvt_s", "fstream.write", "sprintf", "recursive_mutex", "strrchr", "gethostbyaddr", "_wcsupr_s_l", "strcspn", "MD5_Final", "asprintf", "_wcstombs_s_l", "_tcstok", "free", "MD2_Final", "asctime_s", "_alloca", "_wputenv_s", "_wcsset_s", "_wcslwr_s_l", "SHA1_Update", "filebuf.sputc", "filebuf.sputn", "SQLConnect", "ldap_compare", "mbstowcs_s", "HMAC_Final", "pthread_condattr_init", "_ultow_s", "rand", "ofstream.put", "CC_SHA224_Final", "lstrcpynA", "bcopy", "system", "CreateFile*", "wcscpy_s", "_mbsnbcpy*", "open", "_vsnwprintf", "strncpy", "getopt_long", "CC_SHA512_Final", "_vsprintf_s_l", "scanf", "mkdir", "_localtime_s", "_snprintf", "_mbccpy_s_l", "memcmp", "final", "_ultoa_s", "lstrcpyW", "LoadModule", "_swprintf_s_l", "MD5_Update", "_mbsnset_s_l", "_wstrtime_s", "_strnset_s", "lstrcpyA", "_mbsnbcpy_s", "mlock", "IsBadHugeWritePtr", "copy", "_mbsnbcpy_s_l", "wnsprintf", "wcscpy", "ShellExecute", "CC_MD4", "_ultow", "_vsnwprintf_s_l", "lstrcpyn", "CC_SHA1_Final", "vsnprintf", "_mbsnbset_s", "_i64tow", "SHA256_Init", "wvnsprintf", "RegCreateKey", "strtok_s", "_wctime32_s", "_i64toa", "CC_MD5_Final", "wmemcpy", "WinExec", "CreateDirectory*", "CC_SHA256_Update", "_vsnprintf_s_l", "jrand48", "wsprintf", "ldap_rename_ext_s", "filebuf.open", "_wsystem", "SHA256_Update", "_cwscanf_s", "wsprintfW", "_sntscanf", "_splitpath", "fscanf_s", "strpbrk", "wcstombs_s", "wscanf", "_mbsnbcat_s_l", "strcpynA", "pthread_cond_init", "wcsrtombs_s", "_wsopen_s", "CharToOemBuffA", "RIPEMD160_Update", "_tscanf", "HMAC", "StrCCpy", "Connection.connect", "lstrcatn", "_mbstok", "_mbsncpy", "CC_SHA384_Update", "create_directories", "pthread_mutex_unlock", "CFile.Open", "connect", "_vswprintf_s_l", "_snscanf_s_l", "fputc", "_wscanf_s", "_snprintf_s_l", "strtok", "_strtok_s_l", "lstrcatA", "snwscanf", "pthread_mutex_init", "fputs", "CC_SHA384_Init", "_putenv_s", "CharToOemBuffW", "pthread_mutex_trylock", "__wcstoul_internal", "_memccpy", "_snwprintf_s_l", "_strncpy*", "wmemset", "MD4_Init", "*RC4*", "strcpyW", "_ecvt_s", "memcpy_s", "erand48", "IsBadHugeReadPtr", "strcpyA", "HeapReAlloc", "memcpy", "ldap_rename_ext", "fopen_s", "srandom", "_cgetws_s", "_makepath", "SHA256_Final", "remove", "_mbsupr_s", "pthread_mutexattr_init", "__wcstold_internal", "StrCpy", "ldap_delete", "wmemmove_s", "_mkdir", "strcat", "_cscanf_s_l", "StrCAdd", "swprintf_s", "_strnset_s_l", "close", "ldap_delete_ext_s", "ldap_modrdn", "strchr", "_gmtime32_s", "_ftcscat", "lstrcatnA", "_tcsncat", "OemToChar", "mutex", "CharToOem", "strcpy_s", "lstrcatnW", "_wscanf_s_l", "__lxstat64", "memalign", "MD2_Init", "StrCatBuffW", "StrCpyN", "CC_MD5", "StrCpyA", "StrCatBuffA", "StrCpyW", "tmpnam_r", "_vsnprintf", "strcatA", "StrCpyNW", "_mbsnbset_s_l", "EVP_DigestInit", "_stscanf", "CC_MD2", "_tcscat", "StrCpyNA", "xmalloc", "_tcslen", "*MD4*", "vasprintf", "strxfrm", "chmod", "ldap_add_ext", "alloca", "_snscanf_s", "IsBadWritePtr", "swscanf_s", "wmemcpy_s", "_itoa", "_ui64toa_s", "EVP_DigestUpdate", "__wcstol_internal", "_itow", "StrNCatW", "strncat_s", "ualstrcpy", "execvp", "_mbccat", "EVP_MD_CTX_init", "assert", "ofstream.write", "ldap_add", "_sscanf_s_l", "drand48", "CharToOemW", "swscanf", "_itow_s", "RIPEMD160_Init", "CopyMemory", "initstate", "getpwuid", "vsprintf", "_fcvt_s", "CharToOemA", "setuid", "malloc", "StrCatNA", "strcat_s", "srand", "getwd", "_controlfp_s", "olestrcpy", "__wcstod_internal", "_mbsnbcat", "lstrncat", "des_*", "CC_SHA224_Init", "set*", "vsprintf_s", "SHA1_Final", "_umask_s", "gets", "setstate", "wvsprintfW", "LoadLibraryEx", "ofstream.open", "calloc", "_mbstrlen", "_cgets_s", "_sopen_s", "IsBadStringPtr", "wcsncat_s", "add*", "nrand48", "create_directory", "ldap_search_ext", "_i64toa_s", "_ltoa_s", "_cwscanf_s_l", "wmemcmp", "__lxstat", "lstrlen", "pthread_condattr_destroy", "_ftcscpy", "wcstok_s", "__xmknod", "pthread_attr_destroy", "sethostname", "_fscanf_s_l", "StrCatN", "RegEnumKey", "_tcsncpy", "strcatW", "AfxLoadLibrary", "setenv", "tmpnam", "_mbsncat_s_l", "_wstrdate_s", "_wctime64_s", "_i64tow_s", "CC_MD4_Update", "ldap_add_s", "_umask", "CC_SHA1_Update", "_wcsset_s_l", "_mbsupr_s_l", "strstr", "_tsplitpath", "memmove", "_tcscpy", "vsnprintf_s", "strcmp", "wvnsprintfW", "tmpfile", "ldap_modify", "_mbsncat*", "mrand48", "sizeof", "StrCatA", "_ltow_s", "*desencrypt*", "StrCatW", "_mbccpy", "CC_MD2_Init", "RIPEMD160", "ldap_search", "CC_SHA224", "mbsrtowcs_s", "update", "ldap_delete_s", "getnameinfo", "*RC5*", "_wcsncat_s_l", "DriverManager.getConnection", "socket", "_cscanf_s", "ldap_modrdn_s", "_wopen", "CC_SHA256_Final", "_snwprintf*", "MD2_Update", "strcpy", "_strncat_s_l", "CC_MD5_Init", "mbscpy", "wmemmove", "LoadLibraryW", "_mbslen", "*alloc", "_mbsncat_s", "LoadLibraryA", "fopen", "StrLen", "delete", "_splitpath_s", "CreateFileTransacted*", "MD4_Final", "_open", "CC_SHA384", "wcslen", "wcsncat", "_mktemp_s", "pthread_mutexattr_destroy", "_snwscanf_s", "_strset_s", "_wcsncpy_s_l", "CC_MD2_Final", "_mbstok_s_l", "wctomb_s", "MySQL_Driver.connect", "_snwscanf_s_l", "*_des_*", "LoadLibrary", "_swscanf_s_l", "ldap_compare_s", "ldap_compare_ext", "_strlwr_s", "GetEnvironmentVariable", "cuserid", "_mbscat_s", "strspn", "_mbsncpy_s", "ldap_modrdn2", "LeaveCriticalSection", "CopyFile", "getpwd", "sscanf", "creat", "RegSetValue", "ldap_modrdn2_s", "CFile.Close", "*SHA_1*", "pthread_cond_destroy", "CC_SHA512_Update", "*RC2*", "StrNCatA", "_mbsnbcpy", "_mbsnset_s", "crypt", "excel", "_vstprintf", "xstrdup", "wvsprintfA", "getopt", "mkstemp", "_wcsnset_s", "_stprintf", "_sntprintf", "tmpfile_s", "OpenDocumentFile", "_mbsset_s_l", "_strset_s_l", "_strlwr_s_l", "ifstream.open", "xcalloc", "StrNCpyA", "_wctime_s", "CC_SHA224_Update", "_ctime64_s", "MoveFile", "chown", "StrNCpyW", "IsBadReadPtr", "_ui64tow_s", "IsBadCodePtr", "getc", "OracleCommand.ExecuteOracleScalar", "AccessDataSource.Insert", "IDbDataAdapter.FillSchema", "IDbDataAdapter.Update", "GetWindowText*", "SendMessage", "SqlCommand.ExecuteNonQuery", "streambuf.sgetc", "streambuf.sgetn", "OracleCommand.ExecuteScalar", "SqlDataSource.Update", "_Read_s", "IDataAdapter.Fill", "_wgetenv", "_RecordsetPtr.Open*", "AccessDataSource.Delete", "Recordset.Open*", "filebuf.sbumpc", "DDX_*", "RegGetValue", "fstream.read*", "SqlCeCommand.ExecuteResultSet", "SqlCommand.ExecuteXmlReader", "main", "streambuf.sputbackc", "read", "m_lpCmdLine", "CRichEditCtrl.Get*", "istream.putback", "SqlCeCommand.ExecuteXmlReader", "SqlCeCommand.BeginExecuteXmlReader", "filebuf.sgetn", "OdbcDataAdapter.Update", "filebuf.sgetc", "SQLPutData", "recvfrom", "OleDbDataAdapter.FillSchema", "IDataAdapter.FillSchema", "CRichEditCtrl.GetLine", "DbDataAdapter.Update", "SqlCommand.ExecuteReader", "istream.get", "ReceiveFrom", "_main", "fgetc", "DbDataAdapter.FillSchema", "kbhit", "UpdateCommand.Execute*", "Statement.execute", "fgets", "SelectCommand.Execute*", "getch", "OdbcCommand.ExecuteNonQuery", "CDaoQueryDef.Execute", "fstream.getline", "ifstream.getline", "SqlDataAdapter.FillSchema", "OleDbCommand.ExecuteReader", "Statement.execute*", "SqlCeCommand.BeginExecuteNonQuery", "OdbcCommand.ExecuteScalar", "SqlCeDataAdapter.Update", "sendmessage", "mysqlpp.DBDriver", "fstream.peek", "Receive", "CDaoRecordset.Open", "OdbcDataAdapter.FillSchema", "_wgetenv_s", "OleDbDataAdapter.Update", "readsome", "SqlCommand.BeginExecuteXmlReader", "recv", "ifstream.peek", "_Main", "_tmain", "_Readsome_s", "SqlCeCommand.ExecuteReader", "OleDbCommand.ExecuteNonQuery", "fstream.get", "IDbCommand.ExecuteScalar", "filebuf.sputbackc", "IDataAdapter.Update", "streambuf.sbumpc", "InsertCommand.Execute*", "RegQueryValue", "IDbCommand.ExecuteReader", "SqlPipe.ExecuteAndSend", "Connection.Execute*", "getdlgtext", "ReceiveFromEx", "SqlDataAdapter.Update", "RegQueryValueEx", "SQLExecute", "pread", "SqlCommand.BeginExecuteReader", "AfxWinMain", "getchar", "istream.getline", "SqlCeDataAdapter.Fill", "OleDbDataReader.ExecuteReader", "SqlDataSource.Insert", "istream.peek", "SendMessageCallback", "ifstream.read*", "SqlDataSource.Select", "SqlCommand.ExecuteScalar", "SqlDataAdapter.Fill", "SqlCommand.BeginExecuteNonQuery", "getche", "SqlCeCommand.BeginExecuteReader", "getenv", "streambuf.snextc", "Command.Execute*", "_CommandPtr.Execute*", "SendNotifyMessage", "OdbcDataAdapter.Fill", "AccessDataSource.Update", "fscanf", "QSqlQuery.execBatch", "DbDataAdapter.Fill", "cin", "DeleteCommand.Execute*", "QSqlQuery.exec", "PostMessage", "ifstream.get", "filebuf.snextc", "IDbCommand.ExecuteNonQuery", "Winmain", "fread", "getpass", "GetDlgItemTextCCheckListBox.GetCheck", "DISP_PROPERTY_EX", "pread64", "Socket.Receive*", "SACommand.Execute*", "SQLExecDirect", "SqlCeDataAdapter.FillSchema", "DISP_FUNCTION", "OracleCommand.ExecuteNonQuery", "CEdit.GetLine", "OdbcCommand.ExecuteReader", "CEdit.Get*", "AccessDataSource.Select", "OracleCommand.ExecuteReader", "OCIStmtExecute", "getenv_s", "DB2Command.Execute*", "OracleDataAdapter.FillSchema", "OracleDataAdapter.Fill", "CComboBox.Get*", "SqlCeCommand.ExecuteNonQuery", "OracleCommand.ExecuteOracleNonQuery", "mysqlpp.Query", "istream.read*", "CListBox.GetText", "SqlCeCommand.ExecuteScalar", "ifstream.putback", "readlink", "CHtmlEditCtrl.GetDHtmlDocument", "PostThreadMessage", "CListCtrl.GetItemText", "OracleDataAdapter.Update", "OleDbCommand.ExecuteScalar", "stdin", "SqlDataSource.Delete", "OleDbDataAdapter.Fill", "fstream.putback", "IDbDataAdapter.Fill", "_wspawnl", "fwprintf", "sem_wait", "_unlink", "ldap_search_ext_sW", "signal", "PQclear", "PQfinish", "PQexec", "PQresultStatus"};
                clang_visitChildren( cursor, findchild, &apilist );
        }	
        clang_disposeTranslationUnit( unit );
        clang_disposeIndex( index );
        return 0;
}
