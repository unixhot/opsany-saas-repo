export default {
    state: {
        requestTypeList: [
            { name: 'PING', key: '1' },
            { name: 'TCP', key: '2' },
            { name: 'HTTP(S)', key: '3' },
        ],
        scheduleList: [
            { name: '5秒钟（测试用）', key: '0' },
            { name: '1分钟', key: '1' },
            { name: '5分钟', key: '2' },
            { name: '20分钟', key: '3' },
        ],
        IpTypeList: [
            { name: '全部', key: '1' },
            { name: 'IPV4', key: '2' },
            { name: 'IPV6', key: '3' },
        ],
        tcpTypeList: [
            { key: "1", name: '十六进制格式' },
            { key: "2", name: '文本' },
        ],
        requestMethodList: [
            { key: '1', name: 'GET' },
            { key: '2', name: 'POST' },
            { key: '3', name: 'HEAD' },
        ],
    },
    mutations: {


    },
    actions: {

    }
}