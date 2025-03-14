Поможем провайдерам в эпоху дефицита сетевого оборудования, заблокируем самостоятельно ресурсы на своих роутерах и, таким образом, снизим нагрузку на их оборудование!

Зарубежные сервисы пусть знают, что их ресурсы никому не нужны и мы сами у себя их блокируем!

# Списки заблокированных ресурсов
Списки доступны в нескольких форматах:
- RAW - это список доменов и субдоменов
- Dnsmasq-ipset - список для Dnsmasq в формате ipset (OpenWrt <= 21.02)
- Dnsmasq-nfset - список для Dnsmasq в формате nftables set (OpenWrt >=23.05)

Конфигурация для Dnsmasq добавляет все зарезолвенные IP-адреса в set `vpn-domain`. И можно оперировать этим списком. Заблокировать, конечно же, все эти IP к чертям.

# .dat файлы для Xray
Реализовано в стороннем репозитории
https://github.com/unidcml/allow-domains-dat

# Как заблокировать на своём роутере?
Пример блокировки по списку доменов на роутере с OpenWrt 23.05.

Нужен dnsmasq-full. Загружаем конфиг в tmp/dnsmasq.d. Создаём ipset, все пакеты к ip-адресам из этого ipset будут дропаться.

```
cd /tmp/ && opkg download dnsmasq-full
opkg remove dnsmasq && opkg install dnsmasq-full --cache /tmp/
cp /etc/config/dhcp /etc/config/dhcp-old && mv /etc/config/dhcp-opkg /etc/config/dhcp

cd /tmp/dnsmasq.d && wget https://raw.githubusercontent.com/itdoginfo/allow-domains/main/Russia/inside-dnsmasq-nfset.lst -O domains.conf

uci add firewall ipset
uci set firewall.@ipset[-1].name='vpn_domains'
uci set firewall.@ipset[-1].match='dst_net'
uci add firewall rule
uci set firewall.@rule[-1]=rule
uci set firewall.@rule[-1].name='block_domains'
uci set firewall.@rule[-1].src='lan'
uci set firewall.@rule[-1].dest='*'
uci set firewall.@rule[-1].proto='all'
uci set firewall.@rule[-1].ipset='vpn_domains'
uci set firewall.@rule[-1].family='ipv4'
uci set firewall.@rule[-1].target='DROP'
uci commit

service firewall restart && service dnsmasq restart
```
