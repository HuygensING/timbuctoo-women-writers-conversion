class Pnv_person

    @@categories = [
	"prefix",
	"givenName",
	"patronym",
	"givenNameSuffix",
	"infixTitle",
	"surnamePrefix",
	"baseSurname",
	"trailingPatronym",
	"honorificSuffix",
	"disambiguatingDescription"
    ]

    @@combinations = [
	"surname",
	"literalName",
	"firstName",
	"infix",
	"suffix"
    ]

    @naam = Hash.new

    def initialize
    	@naam = Hash.new
    end
    
    def add categorie,value
    	if @naam[categorie].nil?
    	    @naam[categorie] = value
    	else
    	    @naam[categorie] += " #{value}"
    	    STDERR.puts "added #{categorie} more than once (#{@naam[categorie]})"
    	end
    	STDERR.puts "#{categorie} is unknown as a name part" if !@@categories.include? categorie
    end

    def get categorie
    	return combine categorie if @@combinations.include? categorie
    	return @naam[categorie] unless @@categories.include? categorie
    	return "unknown name part: #{categorie}"
    end

    def combine categorie
    	if categorie.eql?("literalName")
    	    result = ""
    	    @@categories.each do |cat|
        		result += " #{@naam[cat]}"
	        end
	        return clean result
	    elsif categorie.eql?("surname")
	        return clean "#{@naam['surnamePrefix']} #{@naam['baseSurname']}"
	    elsif categorie.eql?("first")
	        return clean "#{@naam['givenName']} #{@naam['patronym']} #{@naam['givenNameSuffix']}"
	    elsif categorie.eql?("infix")
	        return clean "#{@naam['InfixTitle']} #{@naam['surnamePrefix']}"
	    elsif categorie.eql?("suffix")
	        return clean "#{@naam['tralingPatronym']} #{@naam['honorificSuffix']} #{@naam['disambiguatingDescription']}"
	    end
    end

    def clean text
	    text.gsub(/  +/," ").gsub(/' /,"'").strip
    end
    
    def to_h
	    return @naam
    end

    def to_s
	    res = "{\n"
	    @naam.each do |k,v|
	        res += "  #{k} => #{v},\n"
    	end
    	res.strip!
    	res = res[0..-2] if res[-1..-1].eql?(',')
    	res += "}"
    	return res
    end

end

