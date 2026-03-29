-- Pandoc Lua filter: insert page break before every h2 (except first one after h1)
local first_h2 = true

function Header(el)
    if el.level == 2 then
        if first_h2 then
            first_h2 = false
            return el
        end
        local pagebreak = pandoc.RawBlock("openxml",
            '<w:p><w:r><w:br w:type="page"/></w:r></w:p>')
        return {pagebreak, el}
    end
end
