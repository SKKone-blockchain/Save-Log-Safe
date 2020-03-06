pragma solidity >=0.4.22 <0.6.0;

contract LogBank {
    
    event LogLog(string logged, uint256 blocknum);
    event NumberofLogs(uint256 _n, uint256 _max_n);
    
    // check the invalid access of others and log it -> if로 하자꾸나
    modifier watchOut() {
        require(owner == msg.sender);
        _;
    }
    
    //structure for saving log (real log and the block number it has been written on)
    struct Log {
      string log;
      uint256 blocknum;
    }
    
    // nonce, header, ciphertext, tag
    mapping(uint256 => Log) logs;       // backuped logs
    mapping(uint256 => Log) warnings;   // backup warnings
    uint256 n;                          // maximum index of logs
    uint256 wn;                         // warnings index

    address owner;                      // only owner can use this contract
    
    
    constructor () payable public {
        owner = msg.sender;
        n = 0;
        wn = 0;
    }
    
    // get the Log and save it
    function sendLog(string memory _log) public watchOut(){
        require(n + 1 > n);
        logs[n].log = _log;
        logs[n++].blocknum = block.number;
        emit LogLog(_log, block.number);
    }
    
    // return the values "n" and "max_n"
    function getN() public view returns (uint256 _returnn){
        return n;
    }

    // return the log where the index is _i
    function getLogs(uint256 _i) public view returns(string memory _returnlog) {
        require(_i < n);
        return logs[_i].log;
    }
    
        // return the log where the index is _i
    function getLogsInfo(uint256 _i) public view watchOut() returns(string memory _returnlog, uint256 _bnum) {
        require(_i < n);
        return (logs[_i].log, logs[_i].blocknum);
    }

    function warning(string memory _w) public watchOut() {
        warnings[wn].log = _w;
        warnings[wn++].blocknum = block.number;
    }

    function getWN() public view returns(uint256){
        return wn;
    }
    
    function getWarning(uint256 _i) public view returns(string memory, uint256){
        return (warnings[_i].log, warnings[_i].blocknum);
    }
    
    // save the money haha
    function() external payable{
        
    }
    
}
