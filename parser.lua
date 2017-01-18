--[[ nginx server config parser --]]

-- imports
local type = type
local assert = assert
local pairs = pairs
local io_open = io.open
local io_type = io.type
local tinsert = table.insert
local tostring = tostring
local print = print
local string_rep = string.rep
local string_len= string.len


local lpeg = require "lpeg"
lpeg.setmaxstack(600) -- defualt 400
local P, R, S, V, C, Cc, Ct = lpeg.P, lpeg.R, lpeg.S, lpeg.V, lpeg.C, lpeg.Cc, lpeg.Ct


local _M = {}
setfenv(1, _M) -- Remove external access to contain everything in the module

-- dump a table, for debug
function _M.print_t(t)
    local cache = {}
    local function sub_print_r(t,indent)
        if (cache[tostring(t)]) then
            print(indent.."*"..tostring(t))
        else
            cache[tostring(t)]=true
            if (type(t)=="table") then
                for pos,val in pairs(t) do
                    if (type(val)=="table") then
                        print(indent.."["..pos.."] => "..tostring(t).." {")
                        sub_print_r(val,indent..string_rep(" ",string_len(pos)+8))
                        print(indent..string_rep(" ",string_len(pos)+6).."}")
                    elseif (type(val)=="string") then
                        print(indent.."["..pos..'] => "'..val..'"')
                    else
                        print(indent.."["..pos.."] => "..tostring(val))
                    end
                end
            else
                print(indent..tostring(t))
            end
        end
    end
    if (type(t)=="table") then
        print(tostring(t) .. " {")
        sub_print_r(t, " ")
        print("}")
    else
        sub_print_r(t, " ")
    end
end


-- define patterns
local digit = R('09')
local number = digit ^ 1
local alpha = R('az', 'AZ')
-- 以字母开头的 字母+数字+横线+下划线 字符串
local identiter = alpha * (alpha + S'-_' + digit) ^ 0
-- 不含有'换行','花括号', '分号'的字符
local _string = (1 - S'\r\n\f{;}')^1
-- 不含有'花括号', '分号'的字符
local muti_string = (1 - S'{;}')^1
local non_semicolon = 1 - P";"
local non_parentheses = (1 - S'\r\n\f{;}()')^1
local comment = P'#' * (1 - S'\r\n\f')^0
-- whitespace
local ws = (S'\r\n\f\t ' + comment)^0
-- server_name 可能有 localhost 这样的非域名形式
local domain = identiter * '.' * identiter * ('.' * identiter) ^ 0 + identiter
local d8 = P'1' * digit * digit +
           P'25' * R'05' +
           P'2' * R'04' * digit +
           R'19' * digit +
           digit
local ip = d8 * P'.' * d8 * P'.' * d8 * P'.' * d8
local ip_port = ip * P':' * R'19' * digit^-4
local domian_port = domain * P':' * R'19' * digit^-4


-- define tokens

-- if matched, lpeg.match will return table: { 'name',  'patt matched string'}
local function token(name, patt) return Ct(Cc(name) * C(patt)) end
local token_port = token('port', number)
local token_domains = Ct(Cc('domains') * Ct(C(domain) * (ws * C(domain))^0))
local token_upstreams = token('upstream', ip_port + domian_port + ip + identiter)


-- define grammer

-- listen *:80; listen 80; listen 443 ssl; listen localhost:8000; listen 127.0.0.1:8000;
local listen = ((ip + identiter + "*") * ':')^0 * token_port
local p_listen = 'listen' * ws * listen * ws * identiter^0 * ';'
local p_server_name = 'server_name' * ws * token_domains * ';'
local function command_find(s)
    -- command 只关心 listen 和 server_name 指令
    return p_listen:match(s) or p_server_name:match(s)
end

local p_upstream = 'proxy_pass' * ws * 'http://' * token_upstreams * ';'
local function upstream_match(s)
    return p_upstream:match(s)
end

local grammer = P{
    "server",
    server = ws * "server" * ws * '{' * ws * V'server_block'^0 * '}',
    server_block = V'command'/command_find + V'location',
    location = "location" * ws * S'~*^=@'^0 * ws * _string * ws * '{' * ws * V'location_block'^0 * '}' * ws,
    location_block = V'ifstatment' + V'command'/ upstream_match,
    ifstatment = "if" * ws * "(" * ws * non_parentheses^0 * ")" * ws * "{" * ws * V'command'^0 * '}' * ws,
    command = V'luacommand' + identiter * ws * muti_string^0 * ';' * ws,
    luacommand = alpha^1 * "_by_lua" * ws * non_semicolon^1 * ';' * ws,
}


-- parse config

function _M.parse(file)
    local config
    if io_type(file) then
        config = file:read("*a")
    else
        local f = io_open(file, "r")
        config = f:read("*a")
        f:close()
    end
    -- remove any unuseful line
    -- config = config:gsub("^#[^\n]*\n", "", 1)

    local server_blocks = {}
    for _, server_block in pairs(Ct(Ct(grammer) ^ 1):match(config)) do

        -- each server may has muti domain or upstream
        local scheme
        local domains = {}
        local upstreams = {}

        for _, token in pairs(server_block) do
            if type(token) ~= "table" then
                assert(false, "arg <token> is not a table")
            end

            local t_type, t_value = token[1], token[2]

            if t_type == 'port' then
                if t_value == "80" then
                    scheme = "http"
                elseif t_value == "443" then
                    scheme = "https"
                end

            elseif t_type == 'domains' then
                for _, domain in pairs(t_value) do
                    tinsert(domains, domain)
                end

            elseif t_type == 'upstream' then
                tinsert(upstreams, t_value)
            end
        end

        -- if prase an empty server block
        -- var scheme will be nil
        if scheme then
            local block = {}
            for _, domain in pairs(domains) do
                block[domain] = {}
                block[domain][scheme] = upstreams
            end
            tinsert(server_blocks, block)
        end
    end


    -- result  format:
    -- {  "domain1": {
    --      "scheme": upstreams,
    --      "scheme2": upstreams,
    --    },
    --    "domain2": {...},
    -- }
    if #server_blocks == 1 then
        return server_blocks[1]
    end

    -- 由于每个block 内只能 listen 一个端口
    -- nginx 上只允许 80 和 443 ，所以 block 数量最多为2
    local b1, b2 = server_blocks[1], server_blocks[2]

    if b2 then
        for domian, scheme in pairs(b2) do
            if b1[domian] then
                -- 合并 b1 b2 相同的 domain
                for k, v in pairs(scheme) do
                    b1[domian][k] = v
                end
            else
                b1[domian] = scheme
            end
        end
    end
    return b1
end


return _M
