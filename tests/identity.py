import sys
from web3 import Web3
from ethereum.utils import checksum_encode
from json import loads, dump
from web3.contract import ConciseContract
from time import sleep
from sha3 import keccak_256

abi_for_manager = loads('[{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"CompanyAddresses","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"MerchName","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"name","type":"string"}],"name":"regMerch","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"price","type":"uint256"}],"name":"setFee","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"full","type":"string"},{"name":"short","type":"string"}],"name":"regVender","outputs":[],"payable":true,"stateMutability":"payable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"TokenCompanyAddresses","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"MerchAddress","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"getFee","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"bytes32"}],"name":"MerchId","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"","type":"address"}],"name":"newVendorOwnedToken","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"}]')
abi_for_erc721 = loads('[{"constant":true,"inputs":[],"name":"symbols","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_MerchName","type":"string"},{"name":"_tokenId","type":"uint256"}],"name":"transfer","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"tokenOwner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"accepted","type":"bool"},{"name":"_tokenId","type":"uint256"}],"name":"burn","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"Id","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"Assets","outputs":[{"name":"prop","type":"string"},{"name":"status","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":true,"inputs":[],"name":"full_name","outputs":[{"name":"","type":"string"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"num","type":"uint256"}],"name":"create","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"name":"","type":"address"}],"payable":false,"stateMutability":"view","type":"function"},{"constant":false,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"destroy","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"prop","type":"string"},{"name":"_tokenId","type":"uint256"}],"name":"setProperty","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"_tokenId","type":"uint256"}],"name":"requestBurning","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"constant":false,"inputs":[{"name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function"},{"inputs":[{"name":"manager","type":"address"},{"name":"vender","type":"address"},{"name":"full","type":"string"},{"name":"short","type":"string"}],"payable":false,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"name":"tokenId","type":"uint256"}],"name":"AssetCreated","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"name":"previousOwner","type":"address"},{"indexed":true,"name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"}]')
bytecode_for_deployment = '0x60606040526000600255341561001457600080fd5b336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506100786706f05b59d3b2000061007d640100000000026108f2176401000000009004565b6100e2565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415156100d857600080fd5b8060018190555050565b612620806100f16000396000f3006060604052600436106100af576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff1680632374457b146100b45780633ebce3a71461011b57806359299369146101cd57806369fe0e2d1461022a5780636a93a3221461024d57806380af6958146102e25780638da5cb5b14610394578063c362a01c146103e9578063ced72f871461044c578063db45d4d914610475578063f2fde38b146104b0575b600080fd5b34156100bf57600080fd5b6100d96004808035600019169060200190919050506104e9565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b341561012657600080fd5b610152600480803573ffffffffffffffffffffffffffffffffffffffff1690602001909190505061051c565b6040518080602001828103825283818151815260200191508051906020019080838360005b83811015610192578082015181840152602081019050610177565b50505050905090810190601f1680156101bf5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156101d857600080fd5b610228600480803590602001908201803590602001908080601f016020809104026020016040519081016040528093929190818152602001838380828437820191505050505050919050506105cc565b005b341561023557600080fd5b61024b60048080359060200190919050506108f2565b005b6102e0600480803590602001908201803590602001908080601f0160208091040260200160405190810160405280939291908181526020018383808284378201915050505050509190803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091905050610957565b005b34156102ed57600080fd5b610319600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610d09565b6040518080602001828103825283818151815260200191508051906020019080838360005b8381101561035957808201518184015260208101905061033e565b50505050905090810190601f1680156103865780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561039f57600080fd5b6103a7610db9565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b34156103f457600080fd5b61040a6004808035906020019091905050610dde565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b341561045757600080fd5b61045f610e11565b6040518082815260200191505060405180910390f35b341561048057600080fd5b61049a600480803560001916906020019091905050610e1b565b6040518082815260200191505060405180910390f35b34156104bb57600080fd5b6104e7600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610e33565b005b60036020528060005260406000206000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60076020528060005260406000206000915090508054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105c45780601f10610599576101008083540402835291602001916105c4565b820191906000526020600020905b8154815290600101906020018083116105a757829003601f168201915b505050505081565b604051806000019050604051809103902060001916600760003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020604051808280546001816001161561010002031660029004801561067b5780601f1061065957610100808354040283529182019161067b565b820191906000526020600020905b815481529060010190602001808311610667575b50509150506040518091039020600019161480156107135750604051806000019050604051809103902060001916816040518082805190602001908083835b6020831015156106df57805182526020820191506020810190506020830392506106ba565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390206000191614155b801561079c5750600060056000836040518082805190602001908083835b6020831015156107565780518252602082019150602081019050602083039250610731565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390206000191660001916815260200190815260200160002054145b15156107a757600080fd5b6107bd6001600254610f8890919063ffffffff16565b60028190555060025460056000836040518082805190602001908083835b60208310151561080057805182526020820191506020810190506020830392506107db565b6001836020036101000a038019825116818451168082178552505050505050905001915050604051809103902060001916600019168152602001908152602001600020819055503360066000600254815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555080600760003373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002090805190602001906108ee929190610fa6565b5050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff1614151561094d57600080fd5b8060018190555050565b6000600154341015151561096a57600080fd5b600060036000856040518082805190602001908083835b6020831015156109a65780518252602082019150602081019050602083039250610981565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390206000191660001916815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16141515610a2c57600080fd5b30338484610a38611026565b808573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020018060200180602001838103835285818151815260200191508051906020019080838360005b83811015610add578082015181840152602081019050610ac2565b50505050905090810190601f168015610b0a5780820380516001836020036101000a031916815260200191505b50838103825284818151815260200191508051906020019080838360005b83811015610b43578082015181840152602081019050610b28565b50505050905090810190601f168015610b705780820380516001836020036101000a031916815260200191505b509650505050505050604051809103906000f0801515610b8f57600080fd5b90507f0d9c92413d7fcdb155131b16bb9481e529cdd40985e69a2491fdbaa6206682d181604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390a18060036000856040518082805190602001908083835b602083101515610c2f5780518252602082019150602081019050602083039250610c0a565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390206000191660001916815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555082600460008373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000209080519060200190610d03929190610fa6565b50505050565b60046020528060005260406000206000915090508054600181600116156101000203166002900480601f016020809104026020016040519081016040528092919081815260200182805460018160011615610100020316600290048015610db15780601f10610d8657610100808354040283529160200191610db1565b820191906000526020600020905b815481529060010190602001808311610d9457829003601f168201915b505050505081565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b60066020528060005260406000206000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000600154905090565b60056020528060005260406000206000915090505481565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610e8e57600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614151515610eca57600080fd5b8073ffffffffffffffffffffffffffffffffffffffff166000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff167f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e060405160405180910390a3806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b6000808284019050838110151515610f9c57fe5b8091505092915050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f10610fe757805160ff1916838001178555611015565b82800160010185558215611015579182015b82811115611014578251825591602001919060010190610ff9565b5b5090506110229190611036565b5090565b6040516115998061105c83390190565b61105891905b8082111561105457600081600090555060010161103c565b5090565b9056006060604052600060045534156200001557600080fd5b604051620015993803806200159983398101604052808051906020019091908051906020019091908051820191906020018051820191905050336000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555083600160006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055508160029080519060200190620000e79291906200014b565b508060039080519060200190620001009291906200014b565b50826000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050505050620001fa565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106200018e57805160ff1916838001178555620001bf565b82800160010185558215620001bf579182015b82811115620001be578251825591602001919060010190620001a1565b5b509050620001ce9190620001d2565b5090565b620001f791905b80821115620001f3576000816000905550600101620001d9565b5090565b90565b61138f806200020a6000396000f3006060604052600436106100ba576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806307039ff9146100bf57806312cb70c71461014d5780631caaa487146101b3578063202eead91461021657806339a090c9146102445780634b4a80ba1461026d5780637434488414610375578063780900dc146104035780638da5cb5b14610426578063d092401b1461047b578063d7c4671c146104e1578063f2fde38b14610504575b600080fd5b34156100ca57600080fd5b6100d261053d565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156101125780820151818401526020810190506100f7565b50505050905090810190601f16801561013f5780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561015857600080fd5b6101b1600480803590602001908201803590602001908080601f016020809104026020016040519081016040528093929190818152602001838380828437820191505050505050919080359060200190919050506105db565b005b34156101be57600080fd5b6101d46004808035906020019091905050610814565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b341561022157600080fd5b61024260048080351515906020019091908035906020019091905050610847565b005b341561024f57600080fd5b610257610ab2565b6040518082815260200191505060405180910390f35b341561027857600080fd5b61028e6004808035906020019091905050610ab8565b604051808060200180602001838103835285818151815260200191508051906020019080838360005b838110156102d25780820151818401526020810190506102b7565b50505050905090810190601f1680156102ff5780820380516001836020036101000a031916815260200191505b50838103825284818151815260200191508051906020019080838360005b8381101561033857808201518184015260208101905061031d565b50505050905090810190601f1680156103655780820380516001836020036101000a031916815260200191505b5094505050505060405180910390f35b341561038057600080fd5b610388610c0c565b6040518080602001828103825283818151815260200191508051906020019080838360005b838110156103c85780820151818401526020810190506103ad565b50505050905090810190601f1680156103f55780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561040e57600080fd5b6104246004808035906020019091905050610caa565b005b341561043157600080fd5b610439610d35565b604051808273ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16815260200191505060405180910390f35b341561048657600080fd5b6104df600480803590602001908201803590602001908080601f01602080910402602001604051908101604052809392919081815260200183838082843782019150505050505091908035906020019091905050610d5a565b005b34156104ec57600080fd5b6105026004808035906020019091905050610de4565b005b341561050f57600080fd5b61053b600480803573ffffffffffffffffffffffffffffffffffffffff16906020019091905050610eb6565b005b60038054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105d35780601f106105a8576101008083540402835291602001916105d3565b820191906000526020600020905b8154815290600101906020018083116105b657829003601f168201915b505050505081565b6000813373ffffffffffffffffffffffffffffffffffffffff166005600083815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1614151561064b57600080fd5b600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663db45d4d9856040518082805190602001908083835b6020831015156106bf578051825260208201915060208101905060208303925061069a565b6001836020036101000a03801982511681845116808217855250505050505090500191505060405180910390206040518263ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401808260001916600019168152602001915050602060405180830381600087803b151561074557600080fd5b5af1151561075257600080fd5b50505060405180519050915061080e600160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663c362a01c846040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050602060405180830381600087803b15156107f157600080fd5b5af115156107fe57600080fd5b505050604051805190508461100b565b50505050565b60056020528060005260406000206000915054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff161415156108a257600080fd5b60405180807f6f7574206f662075736500000000000000000000000000000000000000000000815250600a01905060405180910390206000191660066000838152602001908152602001600020600101604051808280546001816001161561010002031660029004801561094d5780601f1061092b57610100808354040283529182019161094d565b820191906000526020600020905b815481529060010190602001808311610939575b505091505060405180910390206000191614151561096a57600080fd5b8115610a4d5760006005600083815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055506040805190810160405280602060405190810160405280600081525081526020016020604051908101604052806000815250815250600660008381526020019081526020016000206000820151816000019080519060200190610a2792919061123e565b506020820151816001019080519060200190610a4492919061123e565b50905050610aae565b6040805190810160405280600c81526020017f696e206f7065726174696f6e0000000000000000000000000000000000000000815250600660008381526020019081526020016000206001019080519060200190610aac9291906112be565b505b5050565b60045481565b6006602052806000526040600020600091509050806000018054600181600116156101000203166002900480601f016020809104026020016040519081016040528092919081815260200182805460018160011615610100020316600290048015610b645780601f10610b3957610100808354040283529160200191610b64565b820191906000526020600020905b815481529060010190602001808311610b4757829003601f168201915b505050505090806001018054600181600116156101000203166002900480601f016020809104026020016040519081016040528092919081815260200182805460018160011615610100020316600290048015610c025780601f10610bd757610100808354040283529160200191610c02565b820191906000526020600020905b815481529060010190602001808311610be557829003601f168201915b5050505050905082565b60028054600181600116156101000203166002900480601f016020809104026020016040519081016040528092919081815260200182805460018160011615610100020316600290048015610ca25780601f10610c7757610100808354040283529160200191610ca2565b820191906000526020600020905b815481529060010190602001808311610c8557829003601f168201915b505050505081565b60008060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610d0757600080fd5b600090505b81811015610d3157610d24610d1f611061565b611087565b8080600101915050610d0c565b5050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1681565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610db557600080fd5b81600660008381526020019081526020016000206000019080519060200190610ddf9291906112be565b505050565b803373ffffffffffffffffffffffffffffffffffffffff166005600083815260200190815260200160002060009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff16141515610e5257600080fd5b6040805190810160405280600a81526020017f6f7574206f662075736500000000000000000000000000000000000000000000815250600660008481526020019081526020016000206001019080519060200190610eb19291906112be565b505050565b6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff163373ffffffffffffffffffffffffffffffffffffffff16141515610f1157600080fd5b600073ffffffffffffffffffffffffffffffffffffffff168173ffffffffffffffffffffffffffffffffffffffff1614151515610f4d57600080fd5b8073ffffffffffffffffffffffffffffffffffffffff166000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff167f8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e060405160405180910390a3806000806101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050565b816005600083815260200190815260200160002060006101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff1602179055505050565b6000611079600160045461122090919063ffffffff16565b600481905550600454905090565b7fe9667cd49094a292b02a1d8555f54c265b42912082c2f32b2050393b06d83598816040518082815260200191505060405180910390a1604080519081016040528060038054600181600116156101000203166002900480601f01602080910402602001604051908101604052809291908181526020018280546001816001161561010002031660029004801561115f5780601f106111345761010080835404028352916020019161115f565b820191906000526020600020905b81548152906001019060200180831161114257829003601f168201915b505050505081526020016040805190810160405280600c81526020017f696e206f7065726174696f6e00000000000000000000000000000000000000008152508152506006600083815260200190815260200160002060008201518160000190805190602001906111d192919061123e565b5060208201518160010190805190602001906111ee92919061123e565b5090505061121d6000809054906101000a900473ffffffffffffffffffffffffffffffffffffffff168261100b565b50565b600080828401905083811015151561123457fe5b8091505092915050565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061127f57805160ff19168380011785556112ad565b828001600101855582156112ad579182015b828111156112ac578251825591602001919060010190611291565b5b5090506112ba919061133e565b5090565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f106112ff57805160ff191683800117855561132d565b8280016001018555821561132d579182015b8281111561132c578251825591602001919060010190611311565b5b50905061133a919061133e565b5090565b61136091905b8082111561135c576000816000905550600101611344565b5090565b905600a165627a7a72305820ac6cb7482b4e3db701dd61ab5f941671e184af14de54c962d8b0850a88c280260029a165627a7a72305820c54669500481f1367bd961ef40ff69153314aef48f030867ec1798596abc1d200029'
args = sys.argv
w3 = Web3()

id = 0
with open('account_id') as num:
    id = int(num.read())
account_address = w3.eth.accounts[id]
w3.personal.unlockAccount(account_address, "", 4)

# if len(args) > 2:
#     args = args[args.index('identity.py'):]
#     with open('account.json') as data:
#         account_data = loads(data.read())
#         account_address = checksum_encode(account_data['account'])
#         passwd = account_data['passwd']
#     w3.personal.unlockAccount(account_address, passwd, 4)

def waitTillMine(txhash):
    sleep(1)
    while w3.eth.getTransactionReceipt(txhash) is None:
        sleep(1)
    if w3.eth.getTransactionReceipt(txhash)['status'] == 0:
        raise Exception("Error while calling a func")

def deploy():
    contract = w3.eth.contract(abi=abi_for_manager, bytecode=bytecode_for_deployment)
    trans_hash = contract.deploy({'from': account_address, 'gas': 4 * 10**6}).hex()
    waitTillMine(trans_hash)
    txn_receipt = w3.eth.getTransactionReceipt(trans_hash)
    contract_address = txn_receipt['contractAddress']
    print('Management contract address: ' + contract_address)
    with open('database.json', 'w') as file:
        dump({"mgmtContract": contract_address}, file)

def getManagementContract():
    with open('database.json') as data:
        mgmt_address = loads(data.read())['mgmtContract']
    contract = w3.eth.contract(address=mgmt_address, abi=abi_for_manager, ContractFactoryClass=ConciseContract)
    return contract

def getERC721Contract():
    with open('database.json') as data:
        token_address = loads(data.read())['tokenContract']
    contract = w3.eth.contract(address=token_address, abi=abi_for_erc721, ContractFactoryClass=ConciseContract)
    return contract

def setFee(new_price):
    contract = getManagementContract()
    txhash = contract.setFee(int(new_price * 10 **18), transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    print("Successfully configured")

def getFee():
    contract = getManagementContract()
    price = contract.getFee()
    print('Service fee: ' + ('%f' % (price / 10**18)).rstrip("0").rstrip('.'))

def regVender(company_name, symbols, fee):
    contract = getManagementContract()
    txhash = contract.regVender(company_name, symbols, transact={'from':account_address, 'gas': 4 * 10**6, 'value': int(fee * 10 **18)})
    waitTillMine(txhash)
    company_address = contract.CompanyAddresses(keccak_256(company_name.encode('utf-8')).digest())
    print("Token contract address: " + company_address)
    with open('database.json') as prev_info:
        data = loads(prev_info.read())
    data["tokenContract"] = company_address
    with open('database.json', 'w') as file:
        dump(data, file)

def create(num):
    contract = getERC721Contract()
    last_id = contract.Id()
    txhash = contract.create(num, transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    for i in range(last_id + 1, num + last_id + 1):
        print(i)

def setProperty(prop, tokenId):
    contract = getERC721Contract()
    txhash = contract.setProperty(prop, tokenId, transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    print("Successfully updated")

def getProperty(tokenId):
    ERC721 = getERC721Contract()
    Manager = getManagementContract()
    owner = Manager.MerchName(ERC721.tokenOwner(tokenId))
    prop = ERC721.Assets(tokenId)[0]
    status = ERC721.Assets(tokenId)[1]
    print('Owner: ' + owner + '\nProperties: ' + prop + '\nStatus: ' + status)

def regMerch(name):
    contract = getManagementContract()
    txhash = contract.regMerch(name, transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    print('Merchant registered')

def TransferToken(to, tokenId):
    contract = getERC721Contract()
    txhash = contract.transfer(to, tokenId, transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    print("Ownership transfered")

def destroy(tokenId):
    contract = getERC721Contract()
    if account_address == contract.tokenOwner(tokenId):
        txhash = contract.requestBurning(tokenId, transact={'from': account_address, 'gas': 4 * 10 ** 6})
        print("Destruction requested")
    else:
        txhash = contract.burn(True, tokenId, transact={'from': account_address, 'gas': 4 * 10**6})
        print("Destruction confirmed")
    waitTillMine(txhash)

def repair(tokenId):
    contract = getERC721Contract()
    txhash = contract.burn(False, tokenId, transact={'from': account_address, 'gas': 4 * 10**6})
    waitTillMine(txhash)
    print("Destruction declined")

# print(getERC721Contract().tokenOwner(2))
# address = getERC721Contract().tokenOwner(2)
# print(getManagementContract().MerchName(address))
# exit()

if args[1] == '--deploy':
    deploy()

if args[1] == '--setfee':
    setFee(float(args[2]))

if args[1] == '--getfee':
    getFee()

if args[1] == '--vendreg':
    company_name, symbols, fee = args[2], args[3], float(args[4])
    regVender(company_name, symbols, fee)

if args[1] == '--create':
    create(int(args[2]))

if args[1] == '--setprop':
    setProperty(args[2], int(args[3]))

if args[1] == '--data':
    getProperty(int(args[2]))

if args[1] == '--merchreg':
    regMerch(args[2])

if args[1] == '--owner':
    TransferToken(args[2], int(args[3]))

if args[1] == '--destroy':
    args[2] = int(args[2])
    destroy(args[2])

if args[1] == '--repair':
    repair(int(args[2]))