"""
Top US Universities Data Collection
"""

def get_top_universities():
    """Returns a list of top US universities with their basic information"""
    universities = [
        # Top 25 Universities (Elite Tier)
        {"rank": 1, "name": "Massachusetts Institute of Technology (MIT)", "location": "Cambridge, MA", "type": "Private"},
        {"rank": 2, "name": "Stanford University", "location": "Stanford, CA", "type": "Private"},
        {"rank": 3, "name": "Harvard University", "location": "Cambridge, MA", "type": "Private"},
        {"rank": 4, "name": "California Institute of Technology", "location": "Pasadena, CA", "type": "Private"},
        {"rank": 5, "name": "Princeton University", "location": "Princeton, NJ", "type": "Private"},
        {"rank": 6, "name": "Yale University", "location": "New Haven, CT", "type": "Private"},
        {"rank": 7, "name": "University of California, Berkeley", "location": "Berkeley, CA", "type": "Public"},
        {"rank": 8, "name": "Columbia University", "location": "New York, NY", "type": "Private"},
        {"rank": 9, "name": "University of Chicago", "location": "Chicago, IL", "type": "Private"},
        {"rank": 10, "name": "Johns Hopkins University", "location": "Baltimore, MD", "type": "Private"},
        {"rank": 11, "name": "University of Pennsylvania", "location": "Philadelphia, PA", "type": "Private"},
        {"rank": 12, "name": "Cornell University", "location": "Ithaca, NY", "type": "Private"},
        {"rank": 13, "name": "University of California, Los Angeles", "location": "Los Angeles, CA", "type": "Public"},
        {"rank": 14, "name": "Northwestern University", "location": "Evanston, IL", "type": "Private"},
        {"rank": 15, "name": "University of Michigan", "location": "Ann Arbor, MI", "type": "Public"},
        {"rank": 16, "name": "Carnegie Mellon University", "location": "Pittsburgh, PA", "type": "Private"},
        {"rank": 17, "name": "University of California, San Diego", "location": "La Jolla, CA", "type": "Public"},
        {"rank": 18, "name": "Duke University", "location": "Durham, NC", "type": "Private"},
        {"rank": 19, "name": "Georgia Institute of Technology", "location": "Atlanta, GA", "type": "Public"},
        {"rank": 20, "name": "University of Washington", "location": "Seattle, WA", "type": "Public"},
        {"rank": 21, "name": "University of Illinois Urbana-Champaign", "location": "Champaign, IL", "type": "Public"},
        {"rank": 22, "name": "University of Wisconsin-Madison", "location": "Madison, WI", "type": "Public"},
        {"rank": 23, "name": "University of Texas at Austin", "location": "Austin, TX", "type": "Public"},
        {"rank": 24, "name": "University of Maryland, College Park", "location": "College Park, MD", "type": "Public"},
        {"rank": 25, "name": "Purdue University", "location": "West Lafayette, IN", "type": "Public"},
        
        # Universities 26-50 (Tier 1)
        {"rank": 26, "name": "University of Southern California", "location": "Los Angeles, CA", "type": "Private"},
        {"rank": 27, "name": "Rice University", "location": "Houston, TX", "type": "Private"},
        {"rank": 28, "name": "University of Virginia", "location": "Charlottesville, VA", "type": "Public"},
        {"rank": 29, "name": "University of Minnesota Twin Cities", "location": "Minneapolis, MN", "type": "Public"},
        {"rank": 30, "name": "New York University", "location": "New York, NY", "type": "Private"},
        {"rank": 31, "name": "Ohio State University", "location": "Columbus, OH", "type": "Public"},
        {"rank": 32, "name": "University of California, Davis", "location": "Davis, CA", "type": "Public"},
        {"rank": 33, "name": "University of California, Santa Barbara", "location": "Santa Barbara, CA", "type": "Public"},
        {"rank": 34, "name": "Pennsylvania State University", "location": "University Park, PA", "type": "Public"},
        {"rank": 35, "name": "University of Florida", "location": "Gainesville, FL", "type": "Public"},
        {"rank": 36, "name": "Vanderbilt University", "location": "Nashville, TN", "type": "Private"},
        {"rank": 37, "name": "Texas A&M University", "location": "College Station, TX", "type": "Public"},
        {"rank": 38, "name": "Rensselaer Polytechnic Institute", "location": "Troy, NY", "type": "Private"},
        {"rank": 39, "name": "University of Pittsburgh", "location": "Pittsburgh, PA", "type": "Public"},
        {"rank": 40, "name": "Boston University", "location": "Boston, MA", "type": "Private"},
        {"rank": 41, "name": "University of Rochester", "location": "Rochester, NY", "type": "Private"},
        {"rank": 42, "name": "University of California, Irvine", "location": "Irvine, CA", "type": "Public"},
        {"rank": 43, "name": "University of Notre Dame", "location": "Notre Dame, IN", "type": "Private"},
        {"rank": 44, "name": "Case Western Reserve University", "location": "Cleveland, OH", "type": "Private"},
        {"rank": 45, "name": "Northeastern University", "location": "Boston, MA", "type": "Private"},
        {"rank": 46, "name": "University of Colorado Boulder", "location": "Boulder, CO", "type": "Public"},
        {"rank": 47, "name": "Virginia Tech", "location": "Blacksburg, VA", "type": "Public"},
        {"rank": 48, "name": "University of Arizona", "location": "Tucson, AZ", "type": "Public"},
        {"rank": 49, "name": "Rutgers University", "location": "New Brunswick, NJ", "type": "Public"},
        {"rank": 50, "name": "Michigan State University", "location": "East Lansing, MI", "type": "Public"},

        # Universities 51-75 (Tier 2)
        {"rank": 51, "name": "University of North Carolina Chapel Hill", "location": "Chapel Hill, NC", "type": "Public"},
        {"rank": 52, "name": "Washington University in St. Louis", "location": "St. Louis, MO", "type": "Private"},
        {"rank": 53, "name": "University of Massachusetts Amherst", "location": "Amherst, MA", "type": "Public"},
        {"rank": 54, "name": "University of Delaware", "location": "Newark, DE", "type": "Public"},
        {"rank": 55, "name": "Arizona State University", "location": "Tempe, AZ", "type": "Public"},
        {"rank": 56, "name": "University of Utah", "location": "Salt Lake City, UT", "type": "Public"},
        {"rank": 57, "name": "University of Connecticut", "location": "Storrs, CT", "type": "Public"},
        {"rank": 58, "name": "Worcester Polytechnic Institute", "location": "Worcester, MA", "type": "Private"},
        {"rank": 59, "name": "North Carolina State University", "location": "Raleigh, NC", "type": "Public"},
        {"rank": 60, "name": "University of Iowa", "location": "Iowa City, IA", "type": "Public"},
        {"rank": 61, "name": "University of California, Santa Cruz", "location": "Santa Cruz, CA", "type": "Public"},
        {"rank": 62, "name": "Colorado School of Mines", "location": "Golden, CO", "type": "Public"},
        {"rank": 63, "name": "University of Illinois Chicago", "location": "Chicago, IL", "type": "Public"},
        {"rank": 64, "name": "Stevens Institute of Technology", "location": "Hoboken, NJ", "type": "Private"},
        {"rank": 65, "name": "University of Oregon", "location": "Eugene, OR", "type": "Public"},
        {"rank": 66, "name": "University of Tennessee", "location": "Knoxville, TN", "type": "Public"},
        {"rank": 67, "name": "George Washington University", "location": "Washington, DC", "type": "Private"},
        {"rank": 68, "name": "University of Kansas", "location": "Lawrence, KS", "type": "Public"},
        {"rank": 69, "name": "University of Kentucky", "location": "Lexington, KY", "type": "Public"},
        {"rank": 70, "name": "Clemson University", "location": "Clemson, SC", "type": "Public"},
        {"rank": 71, "name": "Drexel University", "location": "Philadelphia, PA", "type": "Private"},
        {"rank": 72, "name": "Iowa State University", "location": "Ames, IA", "type": "Public"},
        {"rank": 73, "name": "University of California, Riverside", "location": "Riverside, CA", "type": "Public"},
        {"rank": 74, "name": "University of Miami", "location": "Coral Gables, FL", "type": "Private"},
        {"rank": 75, "name": "University of Missouri", "location": "Columbia, MO", "type": "Public"},

        # Universities 76-100 (Tier 3)
        {"rank": 76, "name": "Oregon State University", "location": "Corvallis, OR", "type": "Public"},
        {"rank": 77, "name": "University of Nebraska-Lincoln", "location": "Lincoln, NE", "type": "Public"},
        {"rank": 78, "name": "University of Oklahoma", "location": "Norman, OK", "type": "Public"},
        {"rank": 79, "name": "University of South Carolina", "location": "Columbia, SC", "type": "Public"},
        {"rank": 80, "name": "Temple University", "location": "Philadelphia, PA", "type": "Public"},
        {"rank": 81, "name": "University of Alabama", "location": "Tuscaloosa, AL", "type": "Public"},
        {"rank": 82, "name": "University of Arkansas", "location": "Fayetteville, AR", "type": "Public"},
        {"rank": 83, "name": "University of Cincinnati", "location": "Cincinnati, OH", "type": "Public"},
        {"rank": 84, "name": "University of Houston", "location": "Houston, TX", "type": "Public"},
        {"rank": 85, "name": "Syracuse University", "location": "Syracuse, NY", "type": "Private"},
        {"rank": 86, "name": "Illinois Institute of Technology", "location": "Chicago, IL", "type": "Private"},
        {"rank": 87, "name": "University of Alabama Birmingham", "location": "Birmingham, AL", "type": "Public"},
        {"rank": 88, "name": "University of Central Florida", "location": "Orlando, FL", "type": "Public"},
        {"rank": 89, "name": "University of Louisville", "location": "Louisville, KY", "type": "Public"},
        {"rank": 90, "name": "University of New Mexico", "location": "Albuquerque, NM", "type": "Public"},
        {"rank": 91, "name": "University of South Florida", "location": "Tampa, FL", "type": "Public"},
        {"rank": 92, "name": "Washington State University", "location": "Pullman, WA", "type": "Public"},
        {"rank": 93, "name": "Wayne State University", "location": "Detroit, MI", "type": "Public"},
        {"rank": 94, "name": "University of Texas Dallas", "location": "Richardson, TX", "type": "Public"},
        {"rank": 95, "name": "University of Vermont", "location": "Burlington, VT", "type": "Public"},
        {"rank": 96, "name": "Florida International University", "location": "Miami, FL", "type": "Public"},
        {"rank": 97, "name": "University of Nevada, Reno", "location": "Reno, NV", "type": "Public"},
        {"rank": 98, "name": "San Diego State University", "location": "San Diego, CA", "type": "Public"},
        {"rank": 99, "name": "University of Rhode Island", "location": "Kingston, RI", "type": "Public"},
        {"rank": 100, "name": "University of Mississippi", "location": "Oxford, MS", "type": "Public"}
    ]
    return universities

def get_common_stem_programs():
    """Returns a list of common STEM master's programs"""
    programs = [
        "Computer Science",
        "Electrical Engineering",
        "Mechanical Engineering",
        "Chemical Engineering",
        "Civil Engineering",
        "Aerospace Engineering",
        "Data Science",
        "Artificial Intelligence",
        "Robotics",
        "Biomedical Engineering",
        "Materials Science and Engineering",
        "Industrial Engineering",
        "Mathematics",
        "Physics",
        "Chemistry",
        "Biotechnology"
    ]
    return programs

if __name__ == "__main__":
    universities = get_top_universities()
    programs = get_common_stem_programs()
    print(f"Loaded {len(universities)} universities and {len(programs)} STEM programs")
