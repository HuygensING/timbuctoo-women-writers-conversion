require 'json'
require './pnv_person.rb'



def find_property value
    result = @properties[value.downcase]
    return result if !result.nil?
    value
end

def do_components elems,indent
    name = Pnv_person.new
    elems.each do |elem|
    	type = find_property elem['type']
    	value = elem['value']
    	name.add type,value
    end
    name.to_h.each do |name_part,value|
    	puts "#{get_indent indent}<pnv:#{name_part}>#{value}</pnv:#{name_part}>"
    end
    puts "#{get_indent indent}<pnv:literalName>#{name.get 'literalName'}</pnv:literalName>"
end

def floruit elem,indent
    puts "#{get_indent indent}<schema:floruit rdf:parseType=\"Resource\">"
    indent += 1
    elem
    text = elem[1..-2]
    while md = text.match(/"([^^"]*)":"([^^"]*)",?/)
#	STDERR.puts "#{md[1]}: #{md[2]}"
        puts "#{get_indent indent}<schema:#{md[1]} rdf:datatype=\"http://www.w3.org/2001/XMLSchema#date\">#{md[2]}</schema:#{md[1]}>"
	    text = md.post_match
    end
    indent -= 1
    puts "#{get_indent indent}</schema:floruit>"
end


def parse_elem k,v,indent=1
#    STDERR.puts "#{k}: #{v} (#{v.class})" if k.eql?("floruit")
    k = k[1..-1] if k[0..0].eql?("^")
    k = k[1..-1] if k[0..0].eql?("@")
    if v.class.eql?(Array)
        puts "#{get_indent indent}<schema:#{k}>"
        puts "#{get_indent(indent + 1)}<rdf:Seq>"
        v.each do |va|
            parse_elem k[0..-2],va,indent + 2
        end
        puts "#{get_indent(indent + 1)}</rdf:Seq>"
        puts "#{get_indent indent}</schema:#{k}>"
    elsif v.class.eql?(Hash)
        if k.eql?("name")
            puts "#{get_indent indent}<pnv:name rdf:parseType=\"Resource\">"
        else
            puts "#{get_indent indent}<schema:#{k} rdf:parseType=\"Resource\">"
        end
        v.each do |ka,va|
            if ka.eql?("components")
                do_components va,indent + 1
            else
                parse_elem ka,va,indent + 1
            end
        end
        if k.eql?("name")
            puts "#{get_indent indent}</pnv:name>"
        else
            puts "#{get_indent indent}</schema:#{k}>"
        end
    else
        if k.eql?("floruit")
            floruit v,indent
        elsif k.downcase.match(/date$/)
            # birthDate deathDate
            puts "#{get_indent indent}<schema:#{k} rdf:datatype=\"http://www.w3.org/2001/XMLSchema#date\">#{v}</schema:#{k}>" unless k.eql?("@type")
        else
	        #  rdf:parseType=\"Literal\"
	        puts "#{get_indent indent}<schema:#{k}>#{v}</schema:#{k}>" unless k.eql?("@type")
	        if k.eql?("displayName")
                puts "#{get_indent indent}<schema:name>#{v}</schema:name>"
            end
        end
    end
end

def get_indent indent
    "  " * indent
end

def scrape_line line
    result = Array.new
    teller = 1

    array = JSON.parse(line)
    array.each do |obj|
#	STDERR.puts JSON.pretty_generate(obj)
    	type =<<EOF
<rdf:Description rdf:about="https://resource.huygens.knaw.nl/ww/#{obj['@type']}/#{obj['_id']}">
  <rdf:type rdf:resource="https://resource.huygens.knaw.nl/ww/#{obj['@type']}" />
EOF
	    puts type
    	obj.each do |k,v|
	        parse_elem k,v
	    end
	    puts "</rdf:Description>"
	    puts
	    teller += 1
#	break if teller > 1
    end
    return !line.eql?("[]")
end



if __FILE__ == $0

    @debug = false

    @properties = {
	"forename" => "givenName",
	"name_link" => "surnamePrefix",
	"surname" => "baseSurname",
	"add_name" => "trailingPatronym",
	"role_name" => "prefix",
	"gen_name" => "givenNameSuffix"
    }

    inputfile = "persons.json"

    begin
	(0..(ARGV.size-1)).each do |i|
	case ARGV[i]
	    when '--debug'
		@debug = true
	    when '-f'
		inputfile = ARGV[i+1]
	    when '-h'
		STDERR.puts "use: ruby read_persons.rb [--debug] [-f inputfile]"
		exit(1)
	end
    end
    rescue => detail
	STDERR.puts "#{detail}"
    end

    header =<<EOF
<?xml version="1.0"?>
<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:schema="http://schema.org/"
    xmlns:pnv="http://www.purl.org/pnv/"
    xmlns:ww="https://resource.huygens.knaw.nl/women_writers/ww"
    xmlns:person="https://resource.huygens.knaw.nl/women_writers/person">

EOF
    puts header
    File.open(inputfile) do |file|
    	while line = file.gets
    	    line.force_encoding(Encoding::UTF_8)
    	    if !line.strip.empty?
    		    scrape_line line
    	    end
    	end
    end

    puts "</rdf:RDF>"

end

