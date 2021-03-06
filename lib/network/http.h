#ifndef __http_h
#define __http_h

#include "httpd.h"
#include "http_file.h"
#include "http_dyn.h"

class eHTTPDynPathResolver;
class eHTTPFilePathResolver;

typedef ePtr<eHTTPDynPathResolver> eHTTPDynPathResolverPtr;
typedef ePtr<eHTTPFilePathResolver> eHTTPFilePathResolverPtr;

class eHTTPServer
{
	eHTTPD m_httpd;
	static eHTTPServer *m_instance;
	eHTTPDynPathResolverPtr m_dyn;
	eHTTPFilePathResolverPtr m_file;
public:
	RESULT getDynResolver(eHTTPDynPathResolverPtr &ptr);
	RESULT getFileResolver(eHTTPFilePathResolverPtr &ptr);
	
	eHTTPServer();
	static eHTTPServer *getInstance() { return m_instance; }
};

#endif
