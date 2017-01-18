local path = "C:\\Users\\web\\PycharmProjects\\openresty-lua-script\\config_parser\\"
local m_package_path = package.path
package.path = string.format("%s;%s?.lua;", m_package_path, path, path)


local p = require("parser")
p.print_t(p.parse("server.conf"))
