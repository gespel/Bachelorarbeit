#include <string.h>
#include <unistd.h>

#include <rte_byteorder.h>

#include <doca_log.h>
#include <doca_flow.h>

#include "flow_common.h"
#include <cjson/cJSON.h>

//#define CLEAR

DOCA_LOG_REGISTER(FLOW_SHARED_COUNTER);

/* Set match l4 port */
#define SET_L4_PORT(layer, port, value) \
	do { \
		if (match.layer.l4_type_ext == DOCA_FLOW_L4_TYPE_EXT_TCP) \
			match.layer.tcp.l4_port.port = (value); \
		else if (match.layer.l4_type_ext == DOCA_FLOW_L4_TYPE_EXT_UDP) \
			match.layer.udp.l4_port.port = (value); \
	} while (0)

void doca_try(doca_error_t result) {

}

static doca_error_t create_shared_counter_pipe(struct doca_flow_port *port,
					       int port_id,
					       enum doca_flow_l4_type_ext out_l4_type,
					       struct doca_flow_pipe **pipe,
						   struct doca_flow_pipe *egress_pipe)
{
	struct doca_flow_match match;
	struct doca_flow_match match_mask;
	struct doca_flow_monitor monitor;
	struct doca_flow_actions actions0, actions1, actions2, *actions_arr[2];
	struct doca_flow_fwd fwd;
	struct doca_flow_pipe_cfg *pipe_cfg;
	doca_error_t result;

	memset(&match, 0, sizeof(match));
	memset(&match_mask, 0, sizeof(match_mask));
	memset(&monitor, 0, sizeof(monitor));
	memset(&actions0, 0, sizeof(actions0));
	memset(&actions1, 0, sizeof(actions1));
	memset(&actions2, 0, sizeof(actions2));
	memset(&fwd, 0, sizeof(fwd));

	/* 5 tuple match */
  	match.outer.l3_type = DOCA_FLOW_L3_TYPE_IP4;
	//match.outer.ip4.src_ip = 0xffffffff;
	match.outer.ip4.src_ip = BE_IPV4_ADDR(255, 255, 255, 255);
	//match.outer.ip4.dst_ip = BE_IPV4_ADDR(255, 255, 255, 255);
	match.outer.l4_type_ext = DOCA_FLOW_L4_TYPE_EXT_UDP;
	//match.outer.udp.l4_port.dst_port = 0xffff;
	SET_L4_PORT(outer, dst_port, 0xffff);
	//SET_L4_PORT(outer, dst_port, 0xffff);

	match_mask.outer.ip4.src_ip = BE_IPV4_ADDR(0, 0, 0, 1);
	//match_mask.outer.l4_type_ext = DOCA_FLOW_L4_TYPE_EXT_UDP;
	match_mask.outer.udp.l4_port.dst_port = 0xffff;


	SET_MAC_ADDR(actions0.outer.eth.dst_mac, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
	SET_MAC_ADDR(actions0.outer.eth.src_mac, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
	//actions0.outer.l3_type = DOCA_FLOW_L3_TYPE_IP4;
	//actions0.outer.ip4.dst_ip = 0xffffffff;

	//actions0.outer.l4_type_ext = DOCA_FLOW_L4_TYPE_EXT_UDP;
	//actions0.outer.udp.l4_port.dst_port = 0xffff;

	//actions_arr[1] = &actions1;
	actions_arr[0] = &actions0;
	//actions_arr[2] = &actions2;

	/* monitor with changeable shared counter ID */
	monitor.counter_type = DOCA_FLOW_RESOURCE_TYPE_SHARED;
	monitor.shared_counter.shared_counter_id = 0xffffffff;

	result = doca_flow_pipe_cfg_create(&pipe_cfg, port);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		return result;
	}

	result = set_flow_pipe_cfg(pipe_cfg, "SHARED_COUNTER_PIPE", DOCA_FLOW_PIPE_BASIC, false);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}
	result = doca_flow_pipe_cfg_set_match(pipe_cfg, &match, &match_mask);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg match: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}
	result = doca_flow_pipe_cfg_set_actions(pipe_cfg, actions_arr, NULL, NULL, 1);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg actions: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}
	result = doca_flow_pipe_cfg_set_monitor(pipe_cfg, &monitor);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg monitor: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}
	//doca_flow_pipe_cfg_set_domain(pipe_cfg, DOCA_FLOW_PIPE_DOMAIN_EGRESS);

	/*result = doca_flow_pipe_cfg_set_domain(pipe_cfg, DOCA_FLOW_PIPE_DOMAIN_EGRESS);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg domain: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}*/

	/* forwarding traffic to other port */
	//fwd.type = DOCA_FLOW_FWD_DROP;
	fwd.type = DOCA_FLOW_FWD_PORT;
	fwd.port_id = 1;
	//fwd.type = DOCA_FLOW_FWD_NONE;
	//fwd.type = DOCA_FLOW_FWD_PIPE;
	//fwd.next_pipe = egress_pipe;

	result = doca_flow_pipe_create(pipe_cfg, &fwd, NULL, pipe);

destroy_pipe_cfg:
	doca_flow_pipe_cfg_destroy(pipe_cfg);
	return result;
}

static doca_error_t add_shared_counter_pipe_entry(struct doca_flow_pipe *pipe,
						  enum doca_flow_l4_type_ext out_l4_type,
						  uint32_t shared_counter_id,
						  struct entries_status *status)
{
	struct doca_flow_match match;
	struct doca_flow_actions actions;
	struct doca_flow_monitor monitor;
	struct doca_flow_pipe_entry *entry_mac;
	struct doca_flow_fwd fwd;

	doca_error_t result;

	memset(&match, 0, sizeof(match));
	memset(&actions, 0, sizeof(actions));
	memset(&monitor, 0, sizeof(monitor));
	memset(&fwd, 0, sizeof(fwd));

	monitor.shared_counter.shared_counter_id = shared_counter_id;

	match.outer.ip4.src_ip = BE_IPV4_ADDR(0, 0, 0, 1);	
	match.outer.l4_type_ext = DOCA_FLOW_L4_TYPE_EXT_UDP;
	match.outer.udp.l4_port.dst_port = rte_cpu_to_be_16(80);

	actions.action_idx = 0;

	SET_MAC_ADDR(actions.outer.eth.dst_mac, 0xa0, 0x88, 0xc2, 0xb6, 0x14, 0x1a);	
	SET_MAC_ADDR(actions.outer.eth.src_mac, 0xc4, 0x70, 0xbd, 0xa0, 0x56, 0xbd);

	result = doca_flow_pipe_add_entry(0, pipe, &match, &actions, &monitor, NULL, 0, status, &entry_mac);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to add entry: %s", doca_error_get_descr(result));
		return result;
	}

	memset(&match, 0, sizeof(match));
	memset(&actions, 0, sizeof(actions));
	memset(&monitor, 0, sizeof(monitor));
	memset(&fwd, 0, sizeof(fwd));

	monitor.shared_counter.shared_counter_id = shared_counter_id;

	match.outer.ip4.src_ip = BE_IPV4_ADDR(0, 0, 0, 0);
	match.outer.l4_type_ext = DOCA_FLOW_L4_TYPE_EXT_UDP;
	match.outer.udp.l4_port.dst_port = rte_cpu_to_be_16(80);

	actions.action_idx = 0;

	SET_MAC_ADDR(actions.outer.eth.dst_mac, 0xa0, 0x88, 0xc2, 0xb5, 0xf4, 0x5a);	
	SET_MAC_ADDR(actions.outer.eth.src_mac, 0xc4, 0x70, 0xbd, 0xa0, 0x56, 0xbd);

	result = doca_flow_pipe_add_entry(0, pipe, &match, &actions, &monitor, NULL, 0, status, &entry_mac);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to add entry 2: %s", doca_error_get_descr(result));
		return result;
	}
	return DOCA_SUCCESS;
}

static doca_error_t create_egress_pipe(struct doca_flow_port *port, struct doca_flow_pipe **pipe)
{
	struct doca_flow_pipe_cfg *pipe_cfg;
	struct doca_flow_monitor monitor;
	doca_error_t result;

	memset(&monitor, 0, sizeof(monitor));

	monitor.counter_type = DOCA_FLOW_RESOURCE_TYPE_NON_SHARED;


	result = doca_flow_pipe_cfg_create(&pipe_cfg, port);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		return result;
	}

	result = set_flow_pipe_cfg(pipe_cfg, "EGRESS_PIPE", DOCA_FLOW_PIPE_CONTROL, true);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}

	result = doca_flow_pipe_cfg_set_monitor(pipe_cfg, &monitor);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg monitor: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}

	result = doca_flow_pipe_create(pipe_cfg, NULL, NULL, pipe);
destroy_pipe_cfg:
	doca_flow_pipe_cfg_destroy(pipe_cfg);
	return result;
}

static doca_error_t create_egress_pipe_entry(struct doca_flow_pipe* pipe, struct entries_status* status) {
	struct doca_flow_match match;

	memset(&match, 0, sizeof(match));

	return doca_flow_pipe_add_entry(0, pipe, &match, NULL, NULL, NULL, 0, status, NULL);
}

static doca_error_t create_control_pipe(struct doca_flow_port *port, struct doca_flow_pipe **pipe)
{
	struct doca_flow_pipe_cfg *pipe_cfg;
	doca_error_t result;

	result = doca_flow_pipe_cfg_create(&pipe_cfg, port);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		return result;
	}

	result = set_flow_pipe_cfg(pipe_cfg, "CONTROL_PIPE", DOCA_FLOW_PIPE_CONTROL, true);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to set doca_flow_pipe_cfg: %s", doca_error_get_descr(result));
		goto destroy_pipe_cfg;
	}

	result = doca_flow_pipe_create(pipe_cfg, NULL, NULL, pipe);
destroy_pipe_cfg:
	doca_flow_pipe_cfg_destroy(pipe_cfg);
	return result;
}

static doca_error_t add_control_pipe_entries(struct doca_flow_pipe *control_pipe,
					     struct doca_flow_pipe *udp_pipe,
					     struct entries_status *status)
{
	struct doca_flow_match match;
	struct doca_flow_fwd fwd;
	uint8_t priority = 0;
	doca_error_t result;

	memset(&match, 0, sizeof(match));
	memset(&fwd, 0, sizeof(fwd));

	match.parser_meta.outer_l3_type = DOCA_FLOW_L3_META_IPV4;
	match.parser_meta.outer_l4_type = DOCA_FLOW_L4_META_UDP;

	fwd.type = DOCA_FLOW_FWD_PIPE;
	fwd.next_pipe = udp_pipe;

	result = doca_flow_pipe_control_add_entry(0,
						  priority,
						  control_pipe,
						  &match,
						  NULL,
						  NULL,
						  NULL,
						  NULL,
						  NULL,
						  NULL,
						  &fwd,
						  status,
						  NULL);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to add control pipe entry: %s", doca_error_get_descr(result));
		return result;
	}

	memset(&match, 0, sizeof(match));
	memset(&fwd, 0, sizeof(fwd));

	return DOCA_SUCCESS;
}

void load_config() {
	FILE *file = fopen("backends.json", "rb");
    if (!file) {
        perror("Fehler beim Öffnen der Datei");
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *content = malloc(length + 1);
    if (!content) {
        perror("Speicherzuweisung fehlgeschlagen");
        fclose(file);
        return NULL;
    }

    fread(content, 1, length, file);
    content[length] = '\0';
    fclose(file);

	cJSON *json = cJSON_Parse(content);
    if (!json) {
        printf("Fehler beim Parsen: %s\n", cJSON_GetErrorPtr());
        return 0;
    }
	printf("%s\n", cJSON_Print(json));

    cJSON *server = cJSON_GetObjectItem(json, "backends");
	if(cJSON_GetArraySize(server) == 0) {
		DOCA_LOG_ERR("No backends found in backends.json!");
		exit(-1);
	}
	cJSON* name = NULL;
  	cJSON* backend_mac = NULL;
	for (int i = 0 ; i < cJSON_GetArraySize(server) ; i++) {
     	cJSON * subitem = cJSON_GetArrayItem(server, i);
     	name = cJSON_GetObjectItem(subitem, "name");
     	backend_mac = cJSON_GetObjectItem(subitem, "mac_address");
		DOCA_LOG_INFO("%s -> %s", name->valuestring, backend_mac->valuestring);
  	}
	usleep(3000000);
	
}

doca_error_t xeno_flow(int nb_queues)
{
	int nb_ports = 1;
	struct flow_resources resource = {1};
	uint32_t nr_shared_resources[SHARED_RESOURCE_NUM_VALUES] = {0};
	//struct doca_flow_port *ports[nb_ports];
	struct doca_flow_port *ports[2];
	//struct doca_flow_port *p0;
	struct doca_dev *dev_arr[nb_ports];
	struct doca_flow_pipe *udp_pipe, *pipe, *egress_pipe;
	int port_id = 0;
	uint32_t shared_counter_ids[] = {0, 1};
	struct doca_flow_resource_query query_results_array[nb_ports];
	struct doca_flow_shared_resource_cfg cfg = {.domain = DOCA_FLOW_PIPE_DOMAIN_DEFAULT};
	struct entries_status status;
	int num_of_entries = 4;
  	doca_error_t result;

	nr_shared_resources[DOCA_FLOW_SHARED_RESOURCE_COUNTER] = 2;

	load_config();


	result = init_doca_flow(nb_queues, "vnf,hws", &resource, nr_shared_resources);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to init DOCA Flow: %s", doca_error_get_descr(result));
		return result;
	}

	//memset(dev_arr, 0, sizeof(struct doca_dev *) * nb_ports);
	memset(dev_arr, 0, sizeof(struct doca_dev *) * 1);
	//result = init_doca_flow_ports(nb_ports, ports, true, dev_arr);
	result = init_doca_flow_ports(2, ports, true, dev_arr);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to init DOCA ports: %s", doca_error_get_descr(result));
		doca_flow_destroy();
		return result;
	}
	memset(&status, 0, sizeof(status));
	result = doca_flow_shared_resource_set_cfg(DOCA_FLOW_SHARED_RESOURCE_COUNTER, 0, &cfg);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to configure shared counter to port %d", 0);
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}
	result = doca_flow_shared_resources_bind(DOCA_FLOW_SHARED_RESOURCE_COUNTER, &shared_counter_ids[0], 1, ports[0]);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to bind shared counter to pipe");
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}
	result = create_shared_counter_pipe(ports[0], 0, DOCA_FLOW_L4_TYPE_EXT_UDP, &udp_pipe, egress_pipe);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create pipe: %s", doca_error_get_descr(result));
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = create_egress_pipe(ports[1], &egress_pipe);
	if(result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create egress pipe!");
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = create_egress_pipe_entry(egress_pipe, &status);
	if(result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to add entry to egress pipe! %s", doca_error_get_descr(result));
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = add_shared_counter_pipe_entry(udp_pipe, DOCA_FLOW_L4_TYPE_EXT_UDP, shared_counter_ids[0], &status);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to add entry: %s", doca_error_get_descr(result));
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = create_control_pipe(ports[0], &pipe);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to create control pipe: %s", doca_error_get_descr(result));
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = add_control_pipe_entries(pipe, udp_pipe, &status);
	if (result != DOCA_SUCCESS) {
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	result = doca_flow_entries_process(ports[0], 0, DEFAULT_TIMEOUT_US, num_of_entries);
	if (result != DOCA_SUCCESS) {
		DOCA_LOG_ERR("Failed to process entries: %s", doca_error_get_descr(result));
		stop_doca_flow_ports(nb_ports, ports);
		doca_flow_destroy();
		return result;
	}

	//DOCA_LOG_INFO("Waiting 5 seconds for test packets to load balance...");
	DOCA_LOG_INFO("Starting the load balancer loop");
	//sleep(5);
  	while(1) {
		result = doca_flow_shared_resources_query(DOCA_FLOW_SHARED_RESOURCE_COUNTER,
							shared_counter_ids,
							query_results_array,
							nb_ports);
		if (result != DOCA_SUCCESS) {
			DOCA_LOG_ERR("Failed to query entry: %s", doca_error_get_descr(result));
			stop_doca_flow_ports(nb_ports, ports);
			doca_flow_destroy();
			return result;
		}

		DOCA_LOG_INFO("Loadbalancer stats:");
		DOCA_LOG_INFO("\tpacket_count: %ld", query_results_array[port_id].counter.total_pkts);
		DOCA_LOG_INFO("\toverall_bytes: %ld", query_results_array[port_id].counter.total_bytes);
		DOCA_LOG_INFO("============================================");

		usleep(500000);
		#ifdef CLEAR
		system("clear");
		#endif
	}

	result = stop_doca_flow_ports(nb_ports, ports);
	doca_flow_destroy();
	return result;
}
