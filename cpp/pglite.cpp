#include "pglite.h"

#include <stdlib.h>

#include <map>
#include <fstream>
#include <iostream>

static std::string get_home_path()
{
#ifdef _WIN32
    return std::string(getenv("HOMEDRIVE")) + std::string(getenv("HOMEPATH"));
#else
    return getenv("HOME");
#endif
}

static std::string ltrim( const std::string& s )
{
    size_t i = 0;
    while ( i < s.size() && isspace(s[i]) ) {
        i++;
    }
    return s.substr(i, s.size() - i);
}

static std::string rtrim( const std::string& s )
{
    int i = s.size() - 1;
    while ( i >= 0 && isspace(s[i]) ) {
        i--;
    }
    return s.substr(0, i + 1);
}

static std::string trim( std::string s )
{
    return rtrim(ltrim(s));
}

static std::map<std::string, std::string> read_config()
{
    std::map<std::string, std::string> conf;
    std::string conf_fn = get_home_path() + "/.pglite/db.conf";
    std::ifstream ifs(conf_fn);
    if ( !ifs.is_open() )
        return conf;
    std::string line;
    while (std::getline(ifs, line)) {
        auto n = line.find('=');
        if ( n != std::string::npos ) {
            conf[trim(line.substr(0, n))] = trim(line.substr(n+1));
        }
    }
    return conf;
}

namespace PGLite
{
std::string cluster_params()
{
    auto c = read_config();
    auto cit = c.find("port");
    if ( cit != c.end() ) {
        return "host=localhost port=" + cit->second;
    }
    return "";
}
}
