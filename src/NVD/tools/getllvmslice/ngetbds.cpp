#include "clang-c/Index.h"
#include <iostream>
#include <string>
#include <cstring>
#include <map>
#include <vector>
using namespace std;

map<string,string> typmap;
int isStruct(string str){
	const char *sch = "struct";
	const char *fch = str.c_str();
	int tag = 0;
	int i = 0;
	int j = 0;
	while(fch[i] != '\0' && sch[j] != '\0'){
		if(fch[i] == sch[j]){
			i++;
			j++;
		}else{
			tag++;
			i = tag;
			j = 0;
		}
	}
	if(sch[j] == '\0')	return 1;
	else	return 0;
}
int isFILE(string str){
	const char *sch = "FILE";
	const char *fch = str.c_str();
	int tag = 0;
	int i = 0;
	int j = 0;
	while(fch[i] != '\0' && sch[j] != '\0'){
		if(fch[i] == sch[j]){
			i++;
			j++;
		}else{
			tag++;
			i = tag;
			j = 0;
		}
	}
	if(sch[j] == '\0')	return 1;
	else	return 0;
}


std::string getCursorSpelling( CXCursor cursor ) {
	CXString cursorSpelling = clang_getCursorSpelling(cursor);
	std::string result      = clang_getCString( cursorSpelling );
	clang_disposeString( cursorSpelling );
	return result;
}
std::string getTypeSpelling( CXCursor cursor ) {
	CXType ctp=clang_getCursorType(cursor);
	CXString cursorSpelling = clang_getTypeSpelling(ctp);
	std::string result      = clang_getCString( cursorSpelling );
	clang_disposeString( cursorSpelling );
	map<string, string>::iterator iter;
	iter = typmap.find(result);
	if(iter != typmap.end()) {
		result = iter->second;
	}
	return result;
}
std::string getCursorSpelling1( CXCursor cursor ) {
	CXString cursorSpelling = clang_getCursorDisplayName( cursor );
	std::string result      = clang_getCString( cursorSpelling );
	clang_disposeString( cursorSpelling );
	return result;
}

void getCursorSpelling2( CXCursor cursor ) {
	/*
	 * clang_getCursorExtent:
	 * Retrieve the physical extent of the source construct referenced by the given cursor.
	 * The extent of a cursor starts with the file/line/column pointing at the first character \
	 * within the source construct that the cursor refers to and ends with the last character within that source construct. 
	 * For a declaration, the extent covers the declaration itself. 
	 */
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
	/*
	 * function: clang_Cursor_getTranslationUnit()
	 * Returns the translation unit that a cursor originated from.
	 */
	CXTranslationUnit TU = clang_Cursor_getTranslationUnit(cursor);
	/*
	 * function: clang_getCXTUResourceUsage()
	 * Return the memory usage of a translation unit.
	 */
	CXTUResourceUsage TUS = clang_getCXTUResourceUsage(TU);
	clang_disposeCXTUResourceUsage(TUS);
	cout << line1 <<  " ";
}

void getCursorSpelling22( CXCursor cursor ) {
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
	cout << line << " "<< line1 <<  " ";
}

std::string getCursorSpelling4( CXCursor cursor ) {
	CXCursorKind cursor1=clang_getCursorKind (cursor);
	CXString c2=clang_getCursorKindSpelling (cursor1);
	string result      = clang_getCString( c2 );
	clang_disposeString( c2);
	return result;
}

CXChildVisitResult functionVisitor(CXCursor cursor, CXCursor parent, CXClientData clientData) {
	CXSourceLocation location = clang_getCursorLocation(cursor);
	CXFile file;
	unsigned int line;
	unsigned int column;
	unsigned int offset;
	clang_getFileLocation(location, &file, &line, &column, &offset);
	if(clang_Location_isFromMainFile(location) == 0) {
		return CXChildVisit_Continue;
	}
	CXCursorKind kind = clang_getCursorKind(cursor);
	CXCursorKind kind1 = clang_getCursorKind(parent);
	string spelling2 = getTypeSpelling(cursor);
	
	string keytag = "(";
	string::size_type tag;
	tag = spelling2.find(keytag);
	if(kind == CXCursorKind::CXCursor_DeclRefExpr && tag == string::npos) { 
		string key1 = "[";
		string key2 = "*";
		string::size_type idx1,idx2;
		idx1=spelling2.find(key1);
		idx2=spelling2.find(key2);
		if ((idx1!=string::npos || idx2!=string::npos) && !isStruct(spelling2) && !isFILE(spelling2)) {
			cout<< "";
		}
		std::string spelling = getCursorSpelling(cursor);
		cout << spelling << " ";         
		return CXChildVisit_Continue;
	}
	return CXChildVisit_Recurse;
}

CXChildVisitResult varjudge(CXCursor cursor, CXCursor parent, CXClientData clientData){
    CXSourceLocation location = clang_getCursorLocation(cursor);
    CXFile file;
    unsigned int line;
    unsigned int column;
    unsigned int offset;
    clang_getFileLocation(location, &file, &line, &column, &offset);
    if(clang_Location_isFromMainFile(location) == 0) {
		return CXChildVisit_Continue;
	}
    CXCursorKind kind = clang_getCursorKind(cursor);
    
    if(kind == CXCursorKind::CXCursor_DeclRefExpr){
        return CXChildVisit_Break;
    }
    
    return CXChildVisit_Recurse;
}

CXChildVisitResult findreturn(CXCursor cursor, CXCursor parent, CXClientData clientData) {
	CXSourceLocation location = clang_getCursorLocation( cursor );
	CXFile file,file1;
	unsigned int line,line1;
	unsigned int column,column1;
	unsigned int offset;
	clang_getFileLocation(location, &file, &line, &column, &offset);
	if( clang_Location_isFromMainFile( location ) == 0) {
		return CXChildVisit_Continue;
	}

	CXCursorKind kind = clang_getCursorKind( cursor );
	std::string spelling5 = getCursorSpelling4( parent );
	CXSourceRange range = clang_getCursorExtent(parent);
	CXSourceLocation location1 = clang_getRangeStart(range);
	clang_getFileLocation(location1, &file1, &line1, &column1, nullptr);
	if(kind == CXCursorKind::CXCursor_ReturnStmt&&spelling5 =="CompoundStmt") {
		cout << line1 << " ";
		getCursorSpelling2( cursor );
	}
	return CXChildVisit_Recurse;

}

CXChildVisitResult findchild(CXCursor cursor, CXCursor parent, CXClientData clientData) {
	CXSourceLocation location = clang_getCursorLocation( cursor );
	CXFile file;
	unsigned int line;
	unsigned int column;
	unsigned int offset;
	clang_getFileLocation(location, &file, &line, &column, &offset);
	//Returns non-zero if the given source location is in the main file of the corresponding translation unit.
	if(clang_Location_isFromMainFile( location ) == 0) {
		return CXChildVisit_Continue;
	}
	auto fileName = clang_getFileName(file);
	
	CXType defctp = clang_getTypedefDeclUnderlyingType(cursor);
	CXString defcursorspelling = clang_getTypeSpelling(defctp);
	string defname = clang_getCString(defcursorspelling);	
	clang_disposeString(defcursorspelling);

	CXType ctp=clang_getCursorType(cursor);
	CXString cursorSpelling = clang_getTypeSpelling(ctp);
	string result = clang_getCString( cursorSpelling );		
	clang_disposeString(cursorSpelling);
	string spelling = getCursorSpelling(cursor);
	if(defname != "" && result!="") { 
		map<string, string>::iterator iter;
		iter = typmap.find(result);
		if(iter == typmap.end()) { 
			typmap.insert(map<string, string>::value_type (result,defname));
		}
	}

	/*
	 * function: clang_getCursorKind()
	 *
 	 * Retrieve the kind of the given cursor.
	 */
	CXCursorKind kind = clang_getCursorKind(cursor);
	CXCursorKind kind1 = clang_getCursorKind(parent);

	CXTranslationUnit tu = clang_Cursor_getTranslationUnit(cursor);
	CXSourceRange range = clang_getCursorExtent(cursor);
	CXToken* tokens;
	unsigned int numTokens;

	// define function
    	if (kind==CXCursorKind::CXCursor_FunctionDecl)   
    	{ 
      		cout << "" << spelling << " " << endl; 
    	}

	// 
    	if(kind == CXCursorKind::CXCursor_CompoundAssignOperator){
		getCursorSpelling2(cursor);
		clang_visitChildren(cursor, functionVisitor, nullptr);
		cout << endl;
		return CXChildVisit_Continue;  
	}

    	//
	else if((kind1 == CXCursorKind::CXCursor_BinaryOperator && kind == CXCursorKind::CXCursor_BinaryOperator)) {

		CXSourceRange range = clang_getCursorExtent(parent);
		CXSourceLocation location = clang_getCursorLocation(parent);
		CXToken *tokens = 0;
		unsigned int nTokens = 0;
		clang_tokenize(tu, range, &tokens, &nTokens);
		for (unsigned int i = 0; i < nTokens; i++)
		{
			CXString s = clang_getTokenSpelling(tu, tokens[i]);
			CXTokenKind kind = clang_getTokenKind(tokens[i]);
			if(kind == CXToken_Punctuation){
				if(strcmp(clang_getCString(s), "=") == 0){
					if(clang_visitChildren(cursor, varjudge, nullptr)){
						getCursorSpelling2(parent);	
						clang_visitChildren(parent, functionVisitor, nullptr);
						cout << endl;
						return CXChildVisit_Continue;
					}
					else{
						break;
					}
					
				}
				else{
					break;
				}
			}
			clang_disposeString(s);
		}
		clang_disposeTokens(tu, tokens, nTokens);
	}
	return CXChildVisit_Recurse;

}

int main(int argc, char** argv) {
	CXIndex index = clang_createIndex(0, 0);
	constexpr const char *ARGUMENTS[] = {};
	CXTranslationUnit  unit = clang_parseTranslationUnit(
	        	index,
	                argv[1],
	                ARGUMENTS,
	                std::extent<decltype(ARGUMENTS)>::value,
	                nullptr,
	                0,
	                CXTranslationUnit_None
	);

	if(unit == nullptr) {
		printf("Unable to parse given file\n");
	} else {
		CXCursor cursor = clang_getTranslationUnitCursor( unit );
		clang_visitChildren( cursor, findchild, nullptr );
	}

	clang_disposeTranslationUnit( unit );
	clang_disposeIndex( index );

	return 0;
}

