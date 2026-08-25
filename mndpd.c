#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/sysinfo.h>
#include <fcntl.h>

#define MNDP_PORT 5678

#define TLV_MAC       0x0001
#define TLV_IDENTITY  0x0005
#define TLV_VERSION   0x0007
#define TLV_PLATFORM  0x0008
#define TLV_UPTIME    0x0009
#define TLV_SOFT_ID   0x000A
#define TLV_BOARD     0x000B
#define TLV_UNPACK    0x000C
#define TLV_INTERFACE 0x0010

static void add_tlv(unsigned char *buf, int *pos, uint16_t type, const void *data, uint16_t len) {
    buf[(*pos)++] = (type >> 8) & 0xFF;
    buf[(*pos)++] = type & 0xFF;
    buf[(*pos)++] = (len >> 8) & 0xFF;
    buf[(*pos)++] = len & 0xFF;
    memcpy(buf + *pos, data, len);
    *pos += len;
}

static int get_mac_address(const char *ifname, unsigned char *mac) {
    int fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (fd < 0) return -1;
    struct ifreq ifr;
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    if (ioctl(fd, SIOCGIFHWADDR, &ifr) < 0) {
        close(fd);
        return -1;
    }
    close(fd);
    memcpy(mac, ifr.ifr_hwaddr.sa_data, 6);
    return 0;
}

static void read_identity(char *out, size_t maxlen) {
    FILE *f = fopen("/etc/config/system", "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof(line), f)) {
            char *p = strstr(line, "hostname");
            if (p) {
                char *val = strchr(p, '\'');
                if (val) {
                    val++;
                    char *end = strchr(val, '\'');
                    if (end) {
                        *end = '\0';
                        snprintf(out, maxlen, "%s", val);
                        fclose(f);
                        return;
                    }
                }
            }
        }
        fclose(f);
    }
    snprintf(out, maxlen, "Delta-LHG5");
}

int main(int argc, char **argv) {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    if (sock < 0) {
        perror("socket");
        return 1;
    }

    int opt = 1;
    setsockopt(sock, SOL_SOCKET, SO_BROADCAST, &opt, sizeof(opt));
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    struct sockaddr_in bind_addr;
    memset(&bind_addr, 0, sizeof(bind_addr));
    bind_addr.sin_family = AF_INET;
    bind_addr.sin_port = htons(MNDP_PORT);
    bind_addr.sin_addr.s_addr = htonl(INADDR_ANY);

    if (bind(sock, (struct sockaddr *)&bind_addr, sizeof(bind_addr)) < 0) {
        perror("bind");
        // Non fatal, continue broadcasting anyway
    }

    // Set non-blocking socket
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);

    struct sockaddr_in bcast_addr;
    memset(&bcast_addr, 0, sizeof(bcast_addr));
    bcast_addr.sin_family = AF_INET;
    bcast_addr.sin_port = htons(MNDP_PORT);
    bcast_addr.sin_addr.s_addr = htonl(INADDR_BROADCAST);

    unsigned char mac[6] = {0x2c, 0xc8, 0x1b, 0x16, 0xbe, 0xde};
    get_mac_address("br-lan", mac) && get_mac_address("eth0", mac);

    while (1) {
        char identity[64] = "Delta-LHG5";
        read_identity(identity, sizeof(identity));

        struct sysinfo si;
        uint32_t uptime = 0;
        if (sysinfo(&si) == 0) uptime = (uint32_t)si.uptime;

        unsigned char packet[512];
        int pos = 0;
        packet[pos++] = 0x00;
        packet[pos++] = 0x00;
        packet[pos++] = 0x00;
        packet[pos++] = 0x00;

        add_tlv(packet, &pos, TLV_MAC, mac, 6);
        add_tlv(packet, &pos, TLV_IDENTITY, identity, strlen(identity));
        add_tlv(packet, &pos, TLV_VERSION, "DeltaOS 1.0 (RouterBOOT)", strlen("DeltaOS 1.0 (RouterBOOT)"));
        add_tlv(packet, &pos, TLV_PLATFORM, "MikroTik", 8);

        uint32_t net_uptime = htonl(uptime);
        add_tlv(packet, &pos, TLV_UPTIME, &net_uptime, 4);
        add_tlv(packet, &pos, TLV_SOFT_ID, "DELTA-LHG", 9);
        add_tlv(packet, &pos, TLV_BOARD, "RBLHG-5nD", 9);

        unsigned char unpack = 1;
        add_tlv(packet, &pos, TLV_UNPACK, &unpack, 1);
        add_tlv(packet, &pos, TLV_INTERFACE, "ether1", 6);

        // Send broadcast announcement
        sendto(sock, packet, pos, 0, (struct sockaddr *)&bcast_addr, sizeof(bcast_addr));

        // Sleep with periodic check for probe queries
        for (int i = 0; i < 50; i++) {
            unsigned char recv_buf[256];
            struct sockaddr_in sender;
            socklen_t sender_len = sizeof(sender);
            int len = recvfrom(sock, recv_buf, sizeof(recv_buf), 0, (struct sockaddr *)&sender, &sender_len);
            if (len > 0) {
                // Reply directly to probe query
                sendto(sock, packet, pos, 0, (struct sockaddr *)&sender, sender_len);
            }
            usleep(100000); // 100ms
        }
    }

    close(sock);
    return 0;
}
