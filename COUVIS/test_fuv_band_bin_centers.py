import os

BAND_BIN_CENTER = """(1115.35, 1116.13, 1116.90, 1117.68, 1118.46, 1119.24, 
    1120.02, 1120.80, 1121.57, 1122.35, 1123.13, 1123.91, 1124.69, 
    1125.47, 1126.24, 1127.02, 1127.80, 1128.58, 1129.36, 1130.14, 
    1130.91, 1131.69, 1132.47, 1133.25, 1134.03, 1134.81, 1135.58, 
    1136.36, 1137.14, 1137.92, 1138.70, 1139.48, 1140.25, 1141.03, 
    1141.81, 1142.59, 1143.37, 1144.15, 1144.93, 1145.70, 1146.48, 
    1147.26, 1148.04, 1148.82, 1149.60, 1150.38, 1151.15, 1151.93, 
    1152.71, 1153.49, 1154.27, 1155.05, 1155.83, 1156.60, 1157.38, 
    1158.16, 1158.94, 1159.72, 1160.50, 1161.28, 1162.05, 1162.83, 
    1163.61, 1164.39, 1165.17, 1165.95, 1166.73, 1167.51, 1168.28, 
    1169.06, 1169.84, 1170.62, 1171.40, 1172.18, 1172.96, 1173.74, 
    1174.51, 1175.29, 1176.07, 1176.85, 1177.63, 1178.41, 1179.19, 
    1179.97, 1180.74, 1181.52, 1182.30, 1183.08, 1183.86, 1184.64, 
    1185.42, 1186.20, 1186.98, 1187.75, 1188.53, 1189.31, 1190.09, 
    1190.87, 1191.65, 1192.43, 1193.21, 1193.99, 1194.76, 1195.54, 
    1196.32, 1197.10, 1197.88, 1198.66, 1199.44, 1200.22, 1201.00, 
    1201.78, 1202.55, 1203.33, 1204.11, 1204.89, 1205.67, 1206.45, 
    1207.23, 1208.01, 1208.79, 1209.57, 1210.34, 1211.12, 1211.90, 
    1212.68, 1213.46, 1214.24, 1215.02, 1215.80, 1216.58, 1217.36, 
    1218.14, 1218.92, 1219.69, 1220.47, 1221.25, 1222.03, 1222.81, 
    1223.59, 1224.37, 1225.15, 1225.93, 1226.71, 1227.49, 1228.27, 
    1229.04, 1229.82, 1230.60, 1231.38, 1232.16, 1232.94, 1233.72, 
    1234.50, 1235.28, 1236.06, 1236.84, 1237.62, 1238.40, 1239.17, 
    1239.95, 1240.73, 1241.51, 1242.29, 1243.07, 1243.85, 1244.63, 
    1245.41, 1246.19, 1246.97, 1247.75, 1248.53, 1249.31, 1250.09, 
    1250.86, 1251.64, 1252.42, 1253.20, 1253.98, 1254.76, 1255.54, 
    1256.32, 1257.10, 1257.88, 1258.66, 1259.44, 1260.22, 1261.00, 
    1261.78, 1262.56, 1263.34, 1264.12, 1264.89, 1265.67, 1266.45, 
    1267.23, 1268.01, 1268.79, 1269.57, 1270.35, 1271.13, 1271.91, 
    1272.69, 1273.47, 1274.25, 1275.03, 1275.81, 1276.59, 1277.37, 
    1278.15, 1278.93, 1279.71, 1280.49, 1281.26, 1282.04, 1282.82, 
    1283.60, 1284.38, 1285.16, 1285.94, 1286.72, 1287.50, 1288.28, 
    1289.06, 1289.84, 1290.62, 1291.40, 1292.18, 1292.96, 1293.74, 
    1294.52, 1295.30, 1296.08, 1296.86, 1297.64, 1298.42, 1299.20, 
    1299.98, 1300.76, 1301.54, 1302.32, 1303.10, 1303.87, 1304.65, 
    1305.43, 1306.21, 1306.99, 1307.77, 1308.55, 1309.33, 1310.11, 
    1310.89, 1311.67, 1312.45, 1313.23, 1314.01, 1314.79, 1315.57, 
    1316.35, 1317.13, 1317.91, 1318.69, 1319.47, 1320.25, 1321.03, 
    1321.81, 1322.59, 1323.37, 1324.15, 1324.93, 1325.71, 1326.49, 
    1327.27, 1328.05, 1328.83, 1329.61, 1330.39, 1331.17, 1331.95, 
    1332.73, 1333.51, 1334.29, 1335.07, 1335.85, 1336.63, 1337.41, 
    1338.19, 1338.97, 1339.75, 1340.53, 1341.31, 1342.09, 1342.87, 
    1343.65, 1344.43, 1345.21, 1345.99, 1346.77, 1347.55, 1348.33, 
    1349.10, 1349.88, 1350.66, 1351.44, 1352.22, 1353.00, 1353.78, 
    1354.56, 1355.34, 1356.12, 1356.90, 1357.68, 1358.46, 1359.24, 
    1360.02, 1360.80, 1361.58, 1362.36, 1363.14, 1363.92, 1364.70, 
    1365.48, 1366.26, 1367.04, 1367.82, 1368.60, 1369.38, 1370.16, 
    1370.94, 1371.72, 1372.50, 1373.28, 1374.06, 1374.84, 1375.62, 
    1376.40, 1377.18, 1377.96, 1378.74, 1379.53, 1380.31, 1381.09, 
    1381.87, 1382.65, 1383.43, 1384.21, 1384.99, 1385.77, 1386.55, 
    1387.33, 1388.11, 1388.89, 1389.67, 1390.45, 1391.23, 1392.01, 
    1392.79, 1393.57, 1394.35, 1395.13, 1395.91, 1396.69, 1397.47, 
    1398.25, 1399.03, 1399.81, 1400.59, 1401.37, 1402.15, 1402.93, 
    1403.71, 1404.49, 1405.27, 1406.05, 1406.83, 1407.61, 1408.39, 
    1409.17, 1409.95, 1410.73, 1411.51, 1412.29, 1413.07, 1413.85, 
    1414.63, 1415.41, 1416.19, 1416.97, 1417.75, 1418.53, 1419.31, 
    1420.09, 1420.87, 1421.65, 1422.43, 1423.21, 1423.99, 1424.77, 
    1425.55, 1426.33, 1427.11, 1427.89, 1428.67, 1429.45, 1430.23, 
    1431.01, 1431.79, 1432.57, 1433.35, 1434.13, 1434.92, 1435.70, 
    1436.48, 1437.26, 1438.04, 1438.82, 1439.60, 1440.38, 1441.16, 
    1441.94, 1442.72, 1443.50, 1444.28, 1445.06, 1445.84, 1446.62, 
    1447.40, 1448.18, 1448.96, 1449.74, 1450.52, 1451.30, 1452.08, 
    1452.86, 1453.64, 1454.42, 1455.20, 1455.98, 1456.76, 1457.54, 
    1458.32, 1459.10, 1459.88, 1460.66, 1461.44, 1462.22, 1463.00, 
    1463.78, 1464.56, 1465.34, 1466.12, 1466.91, 1467.69, 1468.47, 
    1469.25, 1470.03, 1470.81, 1471.59, 1472.37, 1473.15, 1473.93, 
    1474.71, 1475.49, 1476.27, 1477.05, 1477.83, 1478.61, 1479.39, 
    1480.17, 1480.95, 1481.73, 1482.51, 1483.29, 1484.07, 1484.85, 
    1485.63, 1486.41, 1487.19, 1487.97, 1488.75, 1489.53, 1490.31, 
    1491.09, 1491.87, 1492.65, 1493.43, 1494.21, 1495.00, 1495.78, 
    1496.56, 1497.34, 1498.12, 1498.90, 1499.68, 1500.46, 1501.24, 
    1502.02, 1502.80, 1503.58, 1504.36, 1505.14, 1505.92, 1506.70, 
    1507.48, 1508.26, 1509.04, 1509.82, 1510.60, 1511.38, 1512.16, 
    1512.94, 1513.72, 1514.50, 1515.28, 1516.06, 1516.84, 1517.62, 
    1518.40, 1519.18, 1519.96, 1520.74, 1521.52, 1522.31, 1523.09, 
    1523.87, 1524.65, 1525.43, 1526.21, 1526.99, 1527.77, 1528.55, 
    1529.33, 1530.11, 1530.89, 1531.67, 1532.45, 1533.23, 1534.01, 
    1534.79, 1535.57, 1536.35, 1537.13, 1537.91, 1538.69, 1539.47, 
    1540.25, 1541.03, 1541.81, 1542.59, 1543.37, 1544.15, 1544.93, 
    1545.71, 1546.49, 1547.27, 1548.05, 1548.83, 1549.62, 1550.40, 
    1551.18, 1551.96, 1552.74, 1553.52, 1554.30, 1555.08, 1555.86, 
    1556.64, 1557.42, 1558.20, 1558.98, 1559.76, 1560.54, 1561.32, 
    1562.10, 1562.88, 1563.66, 1564.44, 1565.22, 1566.00, 1566.78, 
    1567.56, 1568.34, 1569.12, 1569.90, 1570.68, 1571.46, 1572.24, 
    1573.02, 1573.80, 1574.58, 1575.36, 1576.14, 1576.92, 1577.70, 
    1578.48, 1579.26, 1580.05, 1580.83, 1581.61, 1582.39, 1583.17, 
    1583.95, 1584.73, 1585.51, 1586.29, 1587.07, 1587.85, 1588.63, 
    1589.41, 1590.19, 1590.97, 1591.75, 1592.53, 1593.31, 1594.09, 
    1594.87, 1595.65, 1596.43, 1597.21, 1597.99, 1598.77, 1599.55, 
    1600.33, 1601.11, 1601.89, 1602.67, 1603.45, 1604.23, 1605.01, 
    1605.79, 1606.57, 1607.35, 1608.13, 1608.91, 1609.69, 1610.47, 
    1611.25, 1612.03, 1612.81, 1613.59, 1614.37, 1615.15, 1615.93, 
    1616.71, 1617.49, 1618.27, 1619.05, 1619.83, 1620.61, 1621.40, 
    1622.18, 1622.96, 1623.74, 1624.52, 1625.30, 1626.08, 1626.86, 
    1627.64, 1628.42, 1629.20, 1629.98, 1630.76, 1631.54, 1632.32, 
    1633.10, 1633.88, 1634.66, 1635.44, 1636.22, 1637.00, 1637.78, 
    1638.56, 1639.34, 1640.12, 1640.90, 1641.68, 1642.46, 1643.24, 
    1644.02, 1644.80, 1645.58, 1646.36, 1647.14, 1647.92, 1648.70, 
    1649.48, 1650.26, 1651.04, 1651.82, 1652.60, 1653.38, 1654.16, 
    1654.94, 1655.72, 1656.50, 1657.28, 1658.06, 1658.84, 1659.62, 
    1660.40, 1661.18, 1661.96, 1662.74, 1663.52, 1664.30, 1665.08, 
    1665.86, 1666.64, 1667.42, 1668.20, 1668.98, 1669.76, 1670.54, 
    1671.32, 1672.10, 1672.88, 1673.66, 1674.44, 1675.22, 1676.00, 
    1676.78, 1677.56, 1678.34, 1679.12, 1679.90, 1680.68, 1681.46, 
    1682.24, 1683.02, 1683.80, 1684.58, 1685.36, 1686.14, 1686.92, 
    1687.70, 1688.48, 1689.26, 1690.04, 1690.82, 1691.60, 1692.38, 
    1693.16, 1693.94, 1694.72, 1695.50, 1696.28, 1697.05, 1697.83, 
    1698.61, 1699.39, 1700.17, 1700.95, 1701.73, 1702.51, 1703.29, 
    1704.07, 1704.85, 1705.63, 1706.41, 1707.19, 1707.97, 1708.75, 
    1709.53, 1710.31, 1711.09, 1711.87, 1712.65, 1713.43, 1714.21, 
    1714.99, 1715.77, 1716.55, 1717.33, 1718.11, 1718.89, 1719.67, 
    1720.45, 1721.23, 1722.01, 1722.79, 1723.57, 1724.35, 1725.13, 
    1725.91, 1726.69, 1727.47, 1728.25, 1729.02, 1729.80, 1730.58, 
    1731.36, 1732.14, 1732.92, 1733.70, 1734.48, 1735.26, 1736.04, 
    1736.82, 1737.60, 1738.38, 1739.16, 1739.94, 1740.72, 1741.50, 
    1742.28, 1743.06, 1743.84, 1744.62, 1745.40, 1746.18, 1746.96, 
    1747.74, 1748.52, 1749.29, 1750.07, 1750.85, 1751.63, 1752.41, 
    1753.19, 1753.97, 1754.75, 1755.53, 1756.31, 1757.09, 1757.87, 
    1758.65, 1759.43, 1760.21, 1760.99, 1761.77, 1762.55, 1763.33, 
    1764.11, 1764.88, 1765.66, 1766.44, 1767.22, 1768.00, 1768.78, 
    1769.56, 1770.34, 1771.12, 1771.90, 1772.68, 1773.46, 1774.24, 
    1775.02, 1775.80, 1776.58, 1777.35, 1778.13, 1778.91, 1779.69, 
    1780.47, 1781.25, 1782.03, 1782.81, 1783.59, 1784.37, 1785.15, 
    1785.93, 1786.71, 1787.49, 1788.27, 1789.04, 1789.82, 1790.60, 
    1791.38, 1792.16, 1792.94, 1793.72, 1794.50, 1795.28, 1796.06, 
    1796.84, 1797.62, 1798.40, 1799.17, 1799.95, 1800.73, 1801.51, 
    1802.29, 1803.07, 1803.85, 1804.63, 1805.41, 1806.19, 1806.97, 
    1807.75, 1808.52, 1809.30, 1810.08, 1810.86, 1811.64, 1812.42, 
    1813.20, 1813.98, 1814.76, 1815.54, 1816.32, 1817.09, 1817.87, 
    1818.65, 1819.43, 1820.21, 1820.99, 1821.77, 1822.55, 1823.33, 
    1824.11, 1824.88, 1825.66, 1826.44, 1827.22, 1828.00, 1828.78, 
    1829.56, 1830.34, 1831.12, 1831.90, 1832.67, 1833.45, 1834.23, 
    1835.01, 1835.79, 1836.57, 1837.35, 1838.13, 1838.91, 1839.68, 
    1840.46, 1841.24, 1842.02, 1842.80, 1843.58, 1844.36, 1845.14, 
    1845.92, 1846.69, 1847.47, 1848.25, 1849.03, 1849.81, 1850.59, 
    1851.37, 1852.15, 1852.92, 1853.70, 1854.48, 1855.26, 1856.04, 
    1856.82, 1857.60, 1858.38, 1859.15, 1859.93, 1860.71, 1861.49, 
    1862.27, 1863.05, 1863.83, 1864.60, 1865.38, 1866.16, 1866.94, 
    1867.72, 1868.50, 1869.28, 1870.06, 1870.83, 1871.61, 1872.39, 
    1873.17, 1873.95, 1874.73, 1875.51, 1876.28, 1877.06, 1877.84, 
    1878.62, 1879.40, 1880.18, 1880.95, 1881.73, 1882.51, 1883.29, 
    1884.07, 1884.85, 1885.63, 1886.40, 1887.18, 1887.96, 1888.74, 
    1889.52, 1890.30, 1891.07, 1891.85, 1892.63, 1893.41, 1894.19, 
    1894.97, 1895.74, 1896.52, 1897.30, 1898.08, 1898.86, 1899.64, 
    1900.41, 1901.19, 1901.97, 1902.75, 1903.53, 1904.31, 1905.08, 
    1905.86, 1906.64, 1907.42, 1908.20, 1908.97, 1909.75, 1910.53, 
    1911.31, 1912.09, 1912.87)""".replace('\n', '').replace(' ', '')

for root, dirs, files in os.walk('/Volumes/Migration2/UVIS/pds3-calibration-labels/fuv_calibration'):
    print '...' + root
    for file in files:
        if not file.endswith('.lbl'): continue

        fullpath = os.path.join(root,file)
        with open(fullpath) as f:
            text = f.read().replace('\n', '').replace('\r', '').replace(' ', '')
            if (BAND_BIN_CENTER not in text):
                print fullpath
