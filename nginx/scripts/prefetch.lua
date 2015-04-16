-- Issue a subrequest for a Link header with rel=next

local function absolute_path(base_path, relative_path)
    if string.sub(relative_path, 1, 1) == "/" then return relative_path end
    local path = string.gsub(base_path, "[^/]*$", "")
    path = path .. relative_path
    path = string.gsub(path, "([^/]*%./)", function (s)
        if s ~= "./" then return s else return "" end
    end)
    path = string.gsub(path, "/%.$", "/")
    local reduced
    while reduced ~= path do
        reduced = path
        path = string.gsub(reduced, "([^/]*/%.%./)", function (s)
            if s ~= "../../" then return "" else return s end
        end)
    end
    path = string.gsub(reduced, "([^/]*/%.%.)$", function (s)
        if s ~= "../.." then return "" else return s end
    end)
    return path
end

-- local l = ngx.header["Link"]
-- local url = "prefetch.html"
-- ngx.say("prefetching!")
-- ngx.say(ngx.var.uri)

-- fetch response for original request
local original = "/cache" .. ngx.var.uri
local res = ngx.location.capture(original)
-- local res = ngx.location.capture("/test_index.html")
-- TODO: Check for res.truncated

-- ngx.say("cache_status=", ngx.var.upstream_cache_status)

-- if ngx.var.upstream_cache_status = "MISS"

-- copy the headers from the subrequest to the parent request
for k, v in pairs(res.header) do
    -- ngx.say(k,': ', v)
    if type(v) == "table" then
        ngx.header[k] = table.concat(v, ",")
    else
        ngx.header[k] = v
    end
end

-- Test if a prefix is going to take place after the request is returned
ngx.header.Found_Link = 'False'

local link = ngx.header["Link"]
if(link) then
    ngx.header.Found_Link = 'True'
end

function sleep(n)
    os.execute("sleep " .. tonumber(n))
end

-- Return a result before the prefetching happens, so the client doesn't have to wait for the prefetch as well
-- Otherwise the whole prefetching would be quite useless
if res.status == ngx.HTTP_OK then
    ngx.print(res.body)
else
    ngx.exit(res.status)
end

if(ngx.header["X-Cache-Status"] == "MISS") then
    local link = ngx.header["Link"]
    if(link) then
        local dontcare, first = string.find(link, "<")
        local last, dontcare  = string.find(link, ">")
        local path = string.sub(link, first + 1, last - 1);
        path = absolute_path(ngx.var.uri, path);
        --  ngx.say("Path=", path)

        -- prefetch

        --    local prefetch = "/cache" .. ngx.unescape_uri(path) .. "?prefetch"
        local prefetch = "/cache" .. ngx.unescape_uri(path)
        --  ngx.say("prefetch=", prefetch)
        local res2 = ngx.location.capture(prefetch)
        --  ngx.say("res.headers=", res2.header["Link"])
    end
end

