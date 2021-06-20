import os

from dvbobjects.PSI.PAT import *
from dvbobjects.PSI.NIT import *
from dvbobjects.PSI.SDT import *
from dvbobjects.PSI.PMT import *
from dvbobjects.MHP.AIT import *
from dvbobjects.MHP.Descriptors import *
from dvbobjects.SBTVD.Descriptors import *

def create_tables():
    tvd_ts_id = 0x073b
    tvd_orig_network_id = 0x073b
    ts_freq = 473.143
    ts_remote_control_key = 0x05

    tvd_service_id_sd = 0xe760
    tvd_pmt_pid_sd = 1031

    nit = network_information_section(
        network_id = tvd_orig_network_id,
        network_descriptor_loop = [
            network_descriptor(network_name = "ASTI",),
            system_management_descriptor(
                broadcasting_flag = 0,
                broadcasting_identifier = 3,
                additional_broadcasting_identification = 0x01,
                additional_identification_bytes = [],
            )
        ],
        transport_stream_loop = [
            transport_stream_loop_item(
                transport_stream_id = tvd_ts_id,
                original_network_id = tvd_orig_network_id,
                transport_descriptor_loop = [
                    service_list_descriptor(
                        dvb_service_descriptor_loop = [
                            service_descriptor_loop_item (
                                service_ID = tvd_service_id_sd,
                                service_type = 1,
                            )
                        ]
                    )
                ],
            ),
        terrestrial_delivery_system_descriptor(
            area_code = 1341,
            guard_interval = 0x03,
            transmission_mode = 0x03,
            frequencies = [
                tds_frequency_item(freq=ts_freq)
            ]
        ),
        partial_reception_descriptor (
            service_ids = []
        ),
        transport_stream_information_descriptor(
            remote_control_key_id = ts_remote_control_key,
            ts_name  = "ASTI",
            transmission_type_loop = [
                transmission_type_loop_item(
                    transmission_type_info = 0x0F,
                    service_id_loop = [
                        service_id_loop_item(
                            service_id=tvd_service_id_sd
                    ),
                    ]
                )
            ]
        )
    ],


    version_number = 0,
    section_number = 0,
    last_section_number = 0,
    )


    sdt = service_description_section(
        transport_stream_id = tvd_ts_id,
        original_network_id = tvd_orig_network_id,
        service_loop = [
            service_loop_item(
                service_ID = tvd_service_id_sd,
                EIT_schedule_flag = 0,
                EIT_present_following_flag = 0,
                running_status = 4,
                free_CA_mode = 0,
                service_descriptor_loop = [
                    service_descriptor(
                        service_type = 1,
                        service_provider_name = "",
                        service_name = "ASTI",
                    )
                ]
            )
        ],
        version_number = 0,
        section_number = 0,
        last_section_number = 0,

    )


    pat = program_association_section(
        transport_stream_id = tvd_ts_id,
        program_loop = [
            program_loop_item(
                program_number = 0,
                PID = 16,
            ),
            program_loop_item(
                program_number = tvd_service_id_sd,
                PID = tvd_pmt_pid_sd,
            )
        ],
        version_number = 0,
        section_number = 0,
        last_section_number = 0,
    )

    ait = application_information_section (
        application_type = 0x0009, # GINGA-NCL
        common_descriptor_loop = [],
        application_loop = [
            application_loop_item (
                organisation_id = 0x0000000A,
                application_id = 0x64,
                application_control_code = 0x01, # AUTOSTART
                application_descriptors_loop = [
                transport_protocol_descriptor (
                    protocol_id = 0x0001,
                    transport_protocol_label = 0,
                    remote_connection = 0,
                    component_tag = 0x0C, # association_tag
                ),
                application_descriptor (
                    application_profile = 0x0001,
                    version_major = 1,
                    version_minor = 0,
                    version_micro = 0,
                    service_bound_flag = 1,
                    visibility = 3,
                    application_priority = 1,
                    transport_protocol_labels = [0],
                ),
                application_name_descriptor (
                    application_name = "APP_GINGA"
                ),
                ginga_ncl_application_descriptor (
                    parameters = []
                ),
                ginga_ncl_application_location_descriptor (
                    base_directory = "/",
                    class_path_extension = "",
                    initial_class = "main.ncl", # name of the NCL file
                            # to be executed.
                ),
                ]
            ),
        ],
        version_number = 0,
        section_number = 0,
        last_section_number = 0,
    )

    pmt_sd = program_map_section(
        program_number = tvd_service_id_sd,
        PCR_PID = 2065,
        program_info_descriptor_loop = [],
        stream_loop = [
            stream_loop_item(
                stream_type = 2, #mpeg2 video stream type
                elementary_PID = 2065,
                element_info_descriptor_loop = [
                ]
            ),
            stream_loop_item(
                stream_type = 3, #mpeg2 audio
                elementary_PID = 2075,
                element_info_descriptor_loop = []
            ),
            stream_loop_item (
                stream_type = 5, # AIT stream type
                elementary_PID = 2001,
                element_info_descriptor_loop = [
                    data_component_descriptor (
                        data_component_id = 0xA3, # AIT system
                        additional_data_component_info = ait_identifier_info (
                            application_type = GINGA_NCL_application_type,
                            ait_version = 0
                        ).bytes(),
                    ),
                    application_signalling_descriptor (
                        application_type = 9, # 9 GINGA-NCL
                        AIT_version = 1, # current ait version
                    ),
                ]
            ),
            stream_loop_item (
                stream_type = 0x0B, # DSMCC stream type
                elementary_PID = 2004,
                element_info_descriptor_loop = [
                    association_tag_descriptor (
                        association_tag = 0x0C,
                        use = 0,
                        selector_lenght = 0,
                        transaction_id = 0x80000000,
                        timeout = 0xFFFFFFFF,
                        private_data = "",
                    ),
                    stream_identifier_descriptor (
                        component_tag = 0x0C,
                    ),
                    carousel_identifier_descriptor (
                        carousel_ID = 2,
                        format_ID = 0,
                        private_data = "",
                    ),
                    data_component_descriptor (
                        data_component_id = 0xA0, # GINGA system
                        additional_data_component_info = additional_ginga_j_info (
                            transmission_format = 0x2,
                            document_resolution = 0x5,
                            organization_id = 0x0000000A,
                            application_id = 0x0064,
                            carousel_id = 2,
                        ).bytes(),
                    ),
                ]
            )
    ],     
    version_number = 0,
    section_number = 0,
    last_section_number = 0,
    
    )




    out = open("./nit.sec", "wb")
    out.write(nit.pack())
    out.close()
    os.system("sec2ts 16 < ./nit.sec > ./nit.ts")
    out = open("./pat.sec", "wb")
    out.write(pat.pack())
    out.close()
    os.system("sec2ts 0 < ./pat.sec > ./pat.ts")
    out = open("./sdt.sec", "wb")
    out.write(sdt.pack())
    out.close()
    os.system("sec2ts 17 < ./sdt.sec > ./sdt.ts")
    out = open("./pmt_sd.sec", "wb")
    out.write(pmt_sd.pack())
    out.close()
    os.system("sec2ts " + str(tvd_pmt_pid_sd) +
    " < ./pmt_sd.sec > ./pmt_sd.ts")
    out = open ("./ait.sec", "wb")
    out.write (ait.pack ())
    out.close ()
    os.system ('sec2ts ' + str (2001) + ' <./ait.sec>./ait.ts')
    print "done"

if __name__ == "__main__":
    create_tables()
