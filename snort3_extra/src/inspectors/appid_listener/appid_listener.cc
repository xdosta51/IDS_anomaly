//--------------------------------------------------------------------------
// Copyright (C) 2020-2023 Cisco and/or its affiliates. All rights reserved.
//
// This program is free software; you can redistribute it and/or modify it
// under the terms of the GNU General Public License Version 2 as published
// by the Free Software Foundation.  You may not use, modify or distribute
// this program under any other version of the GNU General Public License.
//
// This program is distributed in the hope that it will be useful, but
// WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
// General Public License for more details.
//
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
//--------------------------------------------------------------------------
// appid_listener.cc author Rajeshwari Adapalam <rajadapa@cisco.com>

//Co-author : Michal Dostal

#include "appid_listener.h"

#include <ctime>

#include "framework/decode_data.h"
#include "framework/inspector.h"
#include "framework/module.h"
#include "main/snort_config.h"
#include "main/snort_types.h"
#include "profiler/profiler.h"
#include "pub_sub/appid_event_ids.h"
#include "pub_sub/http_events.h"
#include "time/packet_time.h"

#include "appid_listener_event_handler.h"

using namespace snort;

/*Edited code*/
const std::string outputFilePath = "/home/mike/snort/prediction/output_predict.txt";


static const char* s_help = "log selected published data to appid_listener.log";

static const Parameter s_params[] =
{
    /*Edited code*/
    { "json_logging", Parameter::PT_BOOL, nullptr, "false",
        "log appid data in json format" },
    { "anomaly_detection", Parameter::PT_BOOL, nullptr, "false",
        "Allow detect anomaly" },
    { "file", Parameter::PT_STRING, nullptr, nullptr,
        "output data to given file" },
    { nullptr, Parameter::PT_MAX, nullptr, nullptr, nullptr }
};

/*Edited code*/
static std::string python_packages = "PYTHONPATH=/home/mike/.local/lib/python3.8/site-packages ";
static std::string python_env = "/usr/bin/python3.8 ";
static std::string prediction_model = "/home/mike/snort/prediction/predict.py ";
static std::string command = python_packages + python_env + prediction_model;

class AppIdListenerModule : public Module
{
public:
    AppIdListenerModule() : Module(MOD_NAME, s_help, s_params) { }

    ~AppIdListenerModule() override
    {
        delete config;
    }

    bool begin(const char*, int, SnortConfig*) override
    {
        if ( config )
            return false;

        config = new AppIdListenerConfig;
        return true;
    }

    bool set(const char*, Value& v, SnortConfig*) override
    {
        if ( v.is("json_logging") )
            config->json_logging = v.get_bool();
        else if ( v.is("file") )
            config->file_name = v.get_string();
        /*Edited code*/
        else if ( v.is("anomaly_detection") )
            config->anomaly_detection = v.get_bool();
        


        return true;
    }

    AppIdListenerConfig* get_data()
    {
        AppIdListenerConfig* temp = config;
        config = nullptr;
        return temp;
    }

private:
    AppIdListenerConfig* config = nullptr;
};

//-------------------------------------------------------------------------
// inspector stuff
//-------------------------------------------------------------------------

class AppIdListenerInspector : public Inspector
{
public:
    AppIdListenerInspector(AppIdListenerModule& mod)
    {
        config = mod.get_data();
        assert(config);
    }

    ~AppIdListenerInspector() override
    { delete config;
        /*Edited Code*/
        if (config->anomaly_detection) {
            std::string new_prediction = command + "\"" + outputer + "\"";
            int returnValue = system(new_prediction.c_str());
            if (WIFEXITED(returnValue))
            {
                for (size_t i = 0; i < stringList.size(); ++i) {
                    std::remove(stringList[i].c_str());
                }

                std::remove(outputer.c_str());
                int exitCode = WEXITSTATUS(returnValue);
                if (exitCode == 1)
                    LogMessage("\n%s\n", "--------------------------------------------------\nAnomalies were detected, log in alerts.json\n--------------------------------------------------\n");
                else 
                    LogMessage("\n%s\n", "--------------------------------------------------\nNo detected anomaly\n--------------------------------------------------\n");
            }
        }
        else {
            std::remove(outputer.c_str());
        }
        /*End of edited code*/

     }

    void eval(Packet*) override { }

    bool configure(SnortConfig* sc) override
    {
        assert(config);
        sc->set_run_flags(RUN_FLAG__TRACK_ON_SYN);
        if (!config->file_name.empty())
        {
            config->file_stream.open(config->file_name);
            if (!config->file_stream.is_open())
                WarningMessage("appid_listener: can't open file %s\n", config->file_name.c_str());
        }
        DataBus::subscribe_network(appid_pub_key, AppIdEventIds::ANY_CHANGE, new AppIdListenerEventHandler(*config));
        return true;
    }

private:
    AppIdListenerConfig* config = nullptr;
};

//-------------------------------------------------------------------------
// api stuff
//-------------------------------------------------------------------------

static Module* mod_ctor()
{
    return new AppIdListenerModule;
}

static void mod_dtor(Module* m)
{
    delete m;
}

static Inspector* al_ctor(Module* m)
{
    assert(m);
    return new AppIdListenerInspector((AppIdListenerModule&)*m);
}

static void al_dtor(Inspector* p)
{
    delete p;
}

static const InspectApi appid_lstnr_api
{
    {
        PT_INSPECTOR,
        sizeof(InspectApi),
        INSAPI_VERSION,
        0,
        API_RESERVED,
        API_OPTIONS,
        MOD_NAME,
        s_help,
        mod_ctor,
        mod_dtor
    },
    IT_PASSIVE,
    PROTO_BIT__NONE,
    nullptr, // buffers
    nullptr, // service
    nullptr, // pinit
    nullptr, // pterm
    nullptr, // tinit,
    nullptr, // tterm,
    al_ctor,
    al_dtor,
    nullptr, // ssn
    nullptr  // reset
};

SO_PUBLIC const BaseApi* snort_plugins[] =
{
    &appid_lstnr_api.base,
    nullptr
};
