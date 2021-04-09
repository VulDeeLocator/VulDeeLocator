#include <iostream>
#include <string>
#include <cstring>
#include "clang-c/Index.h"
using namespace std;

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

CXChildVisitResult functionVisitor(CXCursor cursor, CXCursor parent, CXClientData clientData) {
        CXSourceLocation location = clang_getCursorLocation(cursor);
        if (clang_Location_isFromMainFile(location) == 0) {
                return CXChildVisit_Continue;
        }

        string spelling4 = getCursorSpelling4(cursor);
        string spelling2 = getTypeSpelling(cursor);
        string spelling1 = getCursorSpelling1(cursor);
        string spelling = getCursorSpelling(cursor);
        int a3 = spelling2.size();
        int a1 = spelling1.size();

        string p="*";
        string::size_type idx;
        idx=spelling2.find(p);

        char filename[30]={0};char s[40];char ch;
        if (spelling4=="FunctionDecl")   
        {
                cout<<spelling<<endl;
        }
        string p1="*";
        string::size_type idx1;
        idx1=spelling2.find(p1);
        string p2="[";
        string::size_type idx2;
        idx2=spelling2.find(p2);
        string p3="(";
        string::size_type idx3;
        idx3=spelling2.find(p3);
        string p4=")";
        string::size_type idx4;
        idx4=spelling2.find(p4);
        if (spelling4=="DeclRefExpr"&&(idx2!=string::npos))
        { 
                if(idx3 == string::npos && idx4 == string::npos){
                        getCursorSpelling2( cursor );
                        cout<<spelling1<<endl; 
                }
        }
        return CXChildVisit_Recurse ;
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
        int numDiagnostics = clang_getNumDiagnostics(unit);

        if(unit == nullptr){
                printf("Unable to parse given file\n");
        }
        else{
                CXCursor cursor = clang_getTranslationUnitCursor( unit );
                clang_visitChildren( cursor, functionVisitor, nullptr );
        }
        
        clang_disposeTranslationUnit( unit );
        clang_disposeIndex( index );
        return 0;
}
