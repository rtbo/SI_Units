
#include <si/ElectricResistance.hpp>
#include <si/Energy.hpp>
#include <si/Length.hpp>
#include <si/Mass.hpp>
#include <si/MolarEntropy.hpp>
#include <si/Pressure.hpp>
#include <si/Time.hpp>
#include <si/Velocity.hpp>
#include <si/Operations.hpp>
#include <si/Constants.hpp>

#include "catch.hpp"

#include <sstream>
#include <type_traits>

using namespace si;
using namespace si::literals;

TEST_CASE("Units", "[units]")
{

    SECTION("construction") {
        const auto joules = joule_t{12.0};
        static_assert(std::is_same<decltype(joules)::dim_type, EnergyDim>::value);
        REQUIRE(joules.val() == 12.0);
    }

    SECTION("literal construction") {
        const auto joules = 12_J;
        static_assert(std::is_same<decltype(joules)::dim_type, EnergyDim>::value);
        REQUIRE(joules.val() == 12.0);
    }

    SECTION("assignment") {
        auto joules = joule_t{12.0};
        REQUIRE(joules.val() == 12.0);

        joules = 230_J;
        REQUIRE(joules.val() == 230.0);
    }

    // SECTION("composition") {
    //     const auto distance = 240_m;
    //     const auto duration = 12_s;
    // }

    SECTION("conversion/equality") {
        REQUIRE(10000_g == 10_kg);
    }

    SECTION("comparison") {
        REQUIRE(1400_Pa > 1300_Pa);
        REQUIRE(1000_ohm < 1400_ohm);
        REQUIRE(1e6_J != 1400_J);
    }

    SECTION("printing") {
        std::ostringstream out;
        out << 1350_J_p_molK;
        REQUIRE(out.str() == "1350 J.mol\u207B\u00B9.K\u207B\u00B9");
    }

    SECTION("unary minus") {
        const auto p = 230_Pa;
        const auto pminus = -p;
        REQUIRE(-pminus == p);
        REQUIRE(pminus == pascal_t{-230.0});
    }
}

