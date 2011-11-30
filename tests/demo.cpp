<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=us-ascii" />
<title>libs/serialization/example/demo.cpp - Boost 1.48.0</title>  <link rel="icon" href="/favicon.ico" type="image/ico" />
  <link rel="stylesheet" type="text/css" href="/style-v2/section-doc.css" />
  <!--[if IE 7]> <style type="text/css"> body { behavior: url(/style-v2/csshover3.htc); } </style> <![endif]-->

</head>

<body>
  <div id="heading">
    <div class="heading-inner">
  <div class="heading-placard"></div>

  <h1 class="heading-title">
  <a href="/">
  <img src="/gfx/space.png" alt= "Boost C++ Libraries" class="heading-logo" />
  <span class="heading-boost">Boost</span>
  <span class="heading-cpplibraries">C++ Libraries</span>
  </a></h1>

  <p class="heading-quote">
  <q>...one of the most highly
  regarded and expertly designed C++ library projects in the
  world.</q> <span class="heading-attribution">&mdash; <a href=
  "http://www.gotw.ca/" class="external">Herb Sutter</a> and <a href=
  "http://en.wikipedia.org/wiki/Andrei_Alexandrescu" class="external">Andrei
  Alexandrescu</a>, <a href=
  "http://safari.awprofessional.com/?XmlId=0321113586" class="external">C++
  Coding Standards</a></span></p>

  <div class="heading-sections">
    <ul>
      <li class="welcome-section-tab"><a href="/">Welcome</a></li>

      <li class="boost-section-tab"><a href="/users/">Introduction</a></li>

      <li class="community-section-tab"><a href="/community/">Community</a></li>

      <li class="development-section-tab"><a href=
      "/development/">Development</a></li>

      <li class="support-section-tab"><a href="/support/">Support</a></li>

      <li class="doc-section-tab"><a href="/doc/">Documentation</a></li>

      <li class="map-section-tab"><a href="/map.html">Index</a></li>
    </ul>
  </div>
</div>  </div>

  <div id="body">
    <div id="body-inner">
      <div id="content">
        <div class="section" id="docs">
          <div class="section-0">
            <div class="section-body">
              <h3>libs/serialization/example/demo.cpp</h3>
<pre>
/////////1/////////2/////////3/////////4/////////5/////////6/////////7/////////8
// demo.cpp
//
// (C) Copyright 2002-4 Robert Ramey - http://www.rrsd.com .
// Use, modification and distribution is subject to the Boost Software
// License, Version 1.0. (See accompanying file LICENSE_1_0.txt or copy at
// <a href="http://www.boost.org/LICENSE_1_0.txt">http://www.boost.org/LICENSE_1_0.txt</a>)


#include &lt;cstddef&gt; // NULL
#include &lt;iomanip&gt;
#include &lt;iostream&gt;
#include &lt;fstream&gt;
#include &lt;string&gt;

#include &lt;<a href="../../../boost/archive/tmpdir.hpp">boost/archive/tmpdir.hpp</a>&gt;

#include &lt;<a href="../../../boost/archive/text_iarchive.hpp">boost/archive/text_iarchive.hpp</a>&gt;
#include &lt;<a href="../../../boost/archive/text_oarchive.hpp">boost/archive/text_oarchive.hpp</a>&gt;

#include &lt;<a href="../../../boost/serialization/base_object.hpp">boost/serialization/base_object.hpp</a>&gt;
#include &lt;<a href="../../../boost/serialization/utility.hpp">boost/serialization/utility.hpp</a>&gt;
#include &lt;<a href="../../../boost/serialization/list.hpp">boost/serialization/list.hpp</a>&gt;
#include &lt;<a href="../../../boost/serialization/assume_abstract.hpp">boost/serialization/assume_abstract.hpp</a>&gt;

/////////////////////////////////////////////////////////////
// The intent of this program is to serve as a tutorial for
// users of the serialization package.  An attempt has been made
// to illustrate most of the facilities of the package.  
//
// The intent is to create an example suffciently complete to
// illustrate the usage and utility of the package while
// including a minimum of other code. 
//
// This illustration models the bus system of a small city.
// This includes, multiple bus stops,  bus routes and schedules.
// There are different kinds of stops.  Bus stops in general will
// will appear on multiple routes.  A schedule will include
// muliple trips on the same route.

/////////////////////////////////////////////////////////////
// gps coordinate
//
// llustrates serialization for a simple type
//
class gps_position
{
    friend std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const gps_position &amp;gp);
    friend class boost::serialization::access;
    int degrees;
    int minutes;
    float seconds;
    template&lt;class Archive&gt;
    void serialize(Archive &amp; ar, const unsigned int /* file_version */){
        ar &amp; degrees &amp; minutes &amp; seconds;
    }
public:
    // every serializable class needs a constructor
    gps_position(){};
    gps_position(int _d, int _m, float _s) : 
        degrees(_d), minutes(_m), seconds(_s)
    {}
};
std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const gps_position &amp;gp)
{
    return os &lt;&lt; ' ' &lt;&lt; gp.degrees &lt;&lt; (unsigned char)186 &lt;&lt; gp.minutes &lt;&lt; '\'' &lt;&lt; gp.seconds &lt;&lt; '&quot;';
}

/////////////////////////////////////////////////////////////
// One bus stop
//
// illustrates serialization of serializable members
//

class bus_stop
{
    friend class boost::serialization::access;
    friend std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_stop &amp;gp);
    virtual std::string description() const = 0;
    gps_position latitude;
    gps_position longitude;
    template&lt;class Archive&gt;
    void serialize(Archive &amp;ar, const unsigned int version)
    {
        ar &amp; latitude;
        ar &amp; longitude;
    }
protected:
    bus_stop(const gps_position &amp; _lat, const gps_position &amp; _long) :
        latitude(_lat), longitude(_long)
    {}
public:
    bus_stop(){}
    virtual ~bus_stop(){}
};

BOOST_SERIALIZATION_ASSUME_ABSTRACT(bus_stop)

std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_stop &amp;bs)
{
    return os &lt;&lt; bs.latitude &lt;&lt; bs.longitude &lt;&lt; ' ' &lt;&lt; bs.description();
}

/////////////////////////////////////////////////////////////
// Several kinds of bus stops
//
// illustrates serialization of derived types
//
class bus_stop_corner : public bus_stop
{
    friend class boost::serialization::access;
    std::string street1;
    std::string street2;
    virtual std::string description() const
    {
        return street1 + &quot; and &quot; + street2;
    }
    template&lt;class Archive&gt;
    void serialize(Archive &amp;ar, const unsigned int version)
    {
        // save/load base class information
        ar &amp; boost::serialization::base_object&lt;bus_stop&gt;(*this);
        ar &amp; street1 &amp; street2;
    }

public:
    bus_stop_corner(){}
    bus_stop_corner(const gps_position &amp; _lat, const gps_position &amp; _long,
        const std::string &amp; _s1, const std::string &amp; _s2
    ) :
        bus_stop(_lat, _long), street1(_s1), street2(_s2)
    {
    }
};

class bus_stop_destination : public bus_stop
{
    friend class boost::serialization::access;
    std::string name;
    virtual std::string description() const
    {
        return name;
    }
    template&lt;class Archive&gt;
    void serialize(Archive &amp;ar, const unsigned int version)
    {
        ar &amp; boost::serialization::base_object&lt;bus_stop&gt;(*this) &amp; name;
    }
public:
    
    bus_stop_destination(){}
    bus_stop_destination(
        const gps_position &amp; _lat, const gps_position &amp; _long, const std::string &amp; _name
    ) :
        bus_stop(_lat, _long), name(_name)
    {
    }
};

/////////////////////////////////////////////////////////////
// a bus route is a collection of bus stops
//
// illustrates serialization of STL collection templates.
//
// illustrates serialzation of polymorphic pointer (bus stop *);
//
// illustrates storage and recovery of shared pointers is correct
// and efficient.  That is objects pointed to by more than one
// pointer are stored only once.  In such cases only one such
// object is restored and pointers are restored to point to it
//
class bus_route
{
    friend class boost::serialization::access;
    friend std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_route &amp;br);
    typedef bus_stop * bus_stop_pointer;
    std::list&lt;bus_stop_pointer&gt; stops;
    template&lt;class Archive&gt;
    void serialize(Archive &amp;ar, const unsigned int version)
    {
        // in this program, these classes are never serialized directly but rather
        // through a pointer to the base class bus_stop. So we need a way to be
        // sure that the archive contains information about these derived classes.
        //ar.template register_type&lt;bus_stop_corner&gt;();
        ar.register_type(static_cast&lt;bus_stop_corner *&gt;(NULL));
        //ar.template register_type&lt;bus_stop_destination&gt;();
        ar.register_type(static_cast&lt;bus_stop_destination *&gt;(NULL));
        // serialization of stl collections is already defined
        // in the header
        ar &amp; stops;
    }
public:
    bus_route(){}
    void append(bus_stop *_bs)
    {
        stops.insert(stops.end(), _bs);
    }
};
std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_route &amp;br)
{
    std::list&lt;bus_stop *&gt;::const_iterator it;
    // note: we're displaying the pointer to permit verification
    // that duplicated pointers are properly restored.
    for(it = br.stops.begin(); it != br.stops.end(); it++){
        os &lt;&lt; '\n' &lt;&lt; std::hex &lt;&lt; &quot;0x&quot; &lt;&lt; *it &lt;&lt; std::dec &lt;&lt; ' ' &lt;&lt; **it;
    }
    return os;
}

/////////////////////////////////////////////////////////////
// a bus schedule is a collection of routes each with a starting time
//
// Illustrates serialization of STL objects(pair) in a non-intrusive way.
// See definition of operator&lt;&lt; &lt;pair&lt;F, S&gt; &gt;(ar, pair) and others in
// serialization.hpp
// 
// illustrates nesting of serializable classes
//
// illustrates use of version number to automatically grandfather older
// versions of the same class.

class bus_schedule
{
public:
    // note: this structure was made public. because the friend declarations
    // didn't seem to work as expected.
    struct trip_info
    {
        template&lt;class Archive&gt;
        void serialize(Archive &amp;ar, const unsigned int file_version)
        {
            // in versions 2 or later
            if(file_version &gt;= 2)
                // read the drivers name
                ar &amp; driver;
            // all versions have the follwing info
            ar &amp; hour &amp; minute;
        }

        // starting time
        int hour;
        int minute;
        // only after system shipped was the driver's name added to the class
        std::string driver;

        trip_info(){}
        trip_info(int _h, int _m, const std::string &amp;_d) :
            hour(_h), minute(_m), driver(_d)
        {}
    };
private:
    friend class boost::serialization::access;
    friend std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_schedule &amp;bs);
    friend std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_schedule::trip_info &amp;ti);
    std::list&lt;std::pair&lt;trip_info, bus_route *&gt; &gt; schedule;
    template&lt;class Archive&gt;
    void serialize(Archive &amp;ar, const unsigned int version)
    {
        ar &amp; schedule;
    }
public:
    void append(const std::string &amp;_d, int _h, int _m, bus_route *_br)
    {
        schedule.insert(schedule.end(), std::make_pair(trip_info(_h, _m, _d), _br));
    }
    bus_schedule(){}
};
BOOST_CLASS_VERSION(bus_schedule::trip_info, 2)

std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_schedule::trip_info &amp;ti)
{
    return os &lt;&lt; '\n' &lt;&lt; ti.hour &lt;&lt; ':' &lt;&lt; ti.minute &lt;&lt; ' ' &lt;&lt; ti.driver &lt;&lt; ' ';
}
std::ostream &amp; operator&lt;&lt;(std::ostream &amp;os, const bus_schedule &amp;bs)
{
    std::list&lt;std::pair&lt;bus_schedule::trip_info, bus_route *&gt; &gt;::const_iterator it;
    for(it = bs.schedule.begin(); it != bs.schedule.end(); it++){
        os &lt;&lt; it-&gt;first &lt;&lt; *(it-&gt;second);
    }
    return os;
}

void save_schedule(const bus_schedule &amp;s, const char * filename){
    // make an archive
    std::ofstream ofs(filename);
    boost::archive::text_oarchive oa(ofs);
    oa &lt;&lt; s;
}

void
restore_schedule(bus_schedule &amp;s, const char * filename)
{
    // open the archive
    std::ifstream ifs(filename);
    boost::archive::text_iarchive ia(ifs);

    // restore the schedule from the archive
    ia &gt;&gt; s;
}

int main(int argc, char *argv[])
{   
    // make the schedule
    bus_schedule original_schedule;

    // fill in the data
    // make a few stops
    bus_stop *bs0 = new bus_stop_corner(
        gps_position(34, 135, 52.560f),
        gps_position(134, 22, 78.30f),
        &quot;24th Street&quot;, &quot;10th Avenue&quot;
    );
    bus_stop *bs1 = new bus_stop_corner(
        gps_position(35, 137, 23.456f),
        gps_position(133, 35, 54.12f),
        &quot;State street&quot;, &quot;Cathedral Vista Lane&quot;
    );
    bus_stop *bs2 = new bus_stop_destination(
        gps_position(35, 136, 15.456f),
        gps_position(133, 32, 15.300f),
        &quot;White House&quot;
    );
    bus_stop *bs3 = new bus_stop_destination(
        gps_position(35, 134, 48.789f),
        gps_position(133, 32, 16.230f),
        &quot;Lincoln Memorial&quot;
    );

    // make a  routes
    bus_route route0;
    route0.append(bs0);
    route0.append(bs1);
    route0.append(bs2);

    // add trips to schedule
    original_schedule.append(&quot;bob&quot;, 6, 24, &amp;route0);
    original_schedule.append(&quot;bob&quot;, 9, 57, &amp;route0);
    original_schedule.append(&quot;alice&quot;, 11, 02, &amp;route0);

    // make aother routes
    bus_route route1;
    route1.append(bs3);
    route1.append(bs2);
    route1.append(bs1);

    // add trips to schedule
    original_schedule.append(&quot;ted&quot;, 7, 17, &amp;route1);
    original_schedule.append(&quot;ted&quot;, 9, 38, &amp;route1);
    original_schedule.append(&quot;alice&quot;, 11, 47, &amp;route1);

    // display the complete schedule
    std::cout &lt;&lt; &quot;original schedule&quot;;
    std::cout &lt;&lt; original_schedule;
    
    std::string filename(boost::archive::tmpdir());
    filename += &quot;/demofile.txt&quot;;

    // save the schedule
    save_schedule(original_schedule, filename.c_str());

    // ... some time later
    // make  a new schedule
    bus_schedule new_schedule;

    restore_schedule(new_schedule, filename.c_str());

    // and display
    std::cout &lt;&lt; &quot;\nrestored schedule&quot;;
    std::cout &lt;&lt; new_schedule;
    // should be the same as the old one. (except for the pointer values)

    delete bs0;
    delete bs1;
    delete bs2;
    delete bs3;
    return 0;
}
</pre>
            </div>
          </div>
        </div>
      </div>

      <div class="clear"></div>
    </div>
  </div>

  <div id="footer">
    <div id="footer-left">
      <div id="revised">
        <p>Revised $Date: 2010-09-26 09:11:52 -0400 (Sun, 26 Sep 2010) $</p>
      </div>

      <div id="copyright">
        <p>Copyright Beman Dawes, David Abrahams, 1998-2005.</p>

        <p>Copyright Rene Rivera 2004-2008.</p>
      </div>  <div id="license">
    <p>Distributed under the <a href="/LICENSE_1_0.txt" class=
    "internal">Boost Software License, Version 1.0</a>.</p>
  </div>
    </div>

    <div id="footer-right">
        <div id="banners">
    <p id="banner-xhtml"><a href="http://validator.w3.org/check?uri=referer"
    class="external">XHTML 1.0</a></p>

    <p id="banner-css"><a href=
    "http://jigsaw.w3.org/css-validator/check/referer" class=
    "external">CSS</a></p>

    <p id="banner-osi"><a href=
    "http://www.opensource.org/docs/definition.php" class="external">OSI
    Certified</a></p>
  </div>
    </div>

    <div class="clear"></div>
  </div>
</body>
</html>