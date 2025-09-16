# 智能体开放平台

## Getting Started

### Run by source code

To start the web frontend service, you will need [Node.js v18.x (LTS)](https://nodejs.org/en) and [NPM version 8.x.x](https://www.npmjs.com/) or [Yarn](https://yarnpkg.com/).

First, install the dependencies:

```bash
npm install
# or
yarn install --frozen-lockfile
```

本地项目基于`.env.example`新建一个 `.env.local` 文件:

```
# For production release, change this to PRODUCTION
NEXT_PUBLIC_DEPLOY_ENV=DEVELOPMENT
# The deployment edition, SELF_HOSTED
NEXT_PUBLIC_EDITION=SELF_HOSTED
# The base URL of console application, refers to the Console base URL of WEB service if console domain is
# different from api or web app domain.
# example: http://cloud.dify.ai/console/api
NEXT_PUBLIC_API_PREFIX=http://127.0.0.1:5001/agent-platform/console/api
# The URL for Web APP, refers to the Web App base URL of WEB service if web app domain is different from
# console or api domain.
# example: http://udify.app/api
NEXT_PUBLIC_PUBLIC_API_PREFIX=http://127.0.0.1:5001/agent-platform/api

# SENTRY
NEXT_PUBLIC_SENTRY_DSN=

```

Finally, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000/agent-platform-web-test/apps?console_token=xxxxx](http://localhost:3000/agent-platform-web-test/apps?console_token=xxxx)这里带上启明大模型门户网站的 token.

## Deploy

### Deploy on server

First, build the app for production:

```bash
npm run build
```

Then, start the server:

```bash
npm run start
```

If you want to customize the host and port:

```bash
npm run start --port=3001 --host=0.0.0.0
```

## Lint Code

If your IDE is VSCode, rename `web/.vscode/settings.example.json` to `web/.vscode/settings.json` for lint code setting.

## Documentation

Visit <https://docs.dify.ai/getting-started/readme> to view the full documentation.

## Community

The Dify community can be found on [Discord community](https://discord.gg/5AEfbxcd9k), where you can ask questions, voice ideas, and share your projects.

## 项目结构

```
workflow_frontend
├─ .dockerignore
├─ .editorconfig
├─ .env.example
├─ .eslintignore
├─ .eslintrc.json
├─ .git
│  ├─ COMMIT_EDITMSG
│  ├─ config
│  ├─ description
│  ├─ FETCH_HEAD
│  ├─ HEAD
│  ├─ hooks
│  │  ├─ applypatch-msg.sample
│  │  ├─ commit-msg
│  │  ├─ commit-msg.sample
│  │  ├─ fsmonitor-watchman.sample
│  │  ├─ post-update.sample
│  │  ├─ pre-applypatch.sample
│  │  ├─ pre-commit.sample
│  │  ├─ pre-merge-commit.sample
│  │  ├─ pre-push.sample
│  │  ├─ pre-rebase.sample
│  │  ├─ pre-receive.sample
│  │  ├─ prepare-commit-msg.sample
│  │  ├─ push-to-checkout.sample
│  │  ├─ sendemail-validate.sample
│  │  └─ update.sample
│  ├─ index
│  ├─ info
│  │  └─ exclude
│  ├─ logs
│  │  ├─ HEAD
│  │  └─ refs
│  │     ├─ heads
│  │     │  ├─ fate
│  │     │  │  └─ rag
│  │     │  └─ master
│  │     ├─ remotes
│  │     │  └─ origin
│  │     │     ├─ fate
│  │     │     │  └─ rag
│  │     │     ├─ HEAD
│  │     │     └─ master
│  │     └─ stash
│  ├─ objects
│  │  ├─ 00
│  │  │  └─ 1088dc6f14773df741903a76f5a632b7bac382
│  │  ├─ 01
│  │  │  ├─ 45b495c8acc70ceacbbdafef3fb91c2025e3dd
│  │  │  └─ c7c80a5fed55d3f2e0ddf1f124492ef4a944e7
│  │  ├─ 03
│  │  │  └─ e0e3a297fb0582cdf808385f4791e72031498f
│  │  ├─ 05
│  │  │  ├─ 28356d0a925ff389a696fd104a2c568d641b91
│  │  │  └─ 43253025b4e89919b7ba9fdff5405faa5a3ae0
│  │  ├─ 07
│  │  │  └─ 0f9dcc3b687dac5d6d3633c34bd925e1f47f0a
│  │  ├─ 09
│  │  │  ├─ 2593a976d0ec67a5268907ae5a4361392b740c
│  │  │  ├─ b64de37c06902aed43d1ddd6d0eceb7a6d17a5
│  │  │  ├─ c3123b53128617308095ef6233ef777abc0808
│  │  │  └─ dabf6097888a64e75047d3fa5cf7cf05bf0db3
│  │  ├─ 0a
│  │  │  ├─ bd3ec4ae5cc2299e9faf683c61a046affc03c6
│  │  │  └─ f5fd86b824f01a9401e8faf57b0bb8cc4c1e5f
│  │  ├─ 0b
│  │  │  └─ 868a89fcd627110b81d9665c230f4d42df92af
│  │  ├─ 0c
│  │  │  ├─ 669b53060c7e37f533cd50335e83ebbf259b86
│  │  │  └─ 6add530bb7536e4745c7e5f2a8f7158d89e8aa
│  │  ├─ 0e
│  │  │  └─ 099751e506db5cebf26d28e6fa3365bbed2249
│  │  ├─ 0f
│  │  │  └─ 9310d745b42379eea4847ffbabac921d36b394
│  │  ├─ 10
│  │  │  ├─ 9e07c9b271d86114731070e2ae541133628a71
│  │  │  └─ a17151e0202b58bf572f815175c0957a49cb19
│  │  ├─ 13
│  │  │  └─ 63f374b3c57f481a505b5663dc5324dd96de5c
│  │  ├─ 14
│  │  │  └─ ca45f129fa6548f7f2a31012539bdbecf13215
│  │  ├─ 17
│  │  │  └─ 833d5bf9f36f0d8bceb3472ce6354d22b41f05
│  │  ├─ 18
│  │  │  └─ adfa70f42f07a7dc1b9d2e6e4298f971e05e0e
│  │  ├─ 19
│  │  │  └─ ff12795491a87ce72bdabafdf3956bbb573b2c
│  │  ├─ 1a
│  │  │  └─ 07929b346e0f4187521ad4024bbb233e21d754
│  │  ├─ 1b
│  │  │  └─ 10f5984d3a94e244c43d998ceed0cf6eaa23e1
│  │  ├─ 1c
│  │  │  └─ b6a83ba5eb22bb84d1e58b94ed5460c285533b
│  │  ├─ 1d
│  │  │  └─ e9ab30326215269243216c6b5699938eb3ff2f
│  │  ├─ 1f
│  │  │  └─ 4c8c1aa989e680a36c4a0c5f64d6748683a6da
│  │  ├─ 21
│  │  │  └─ 7b336a6534e307e95908bee31544b801f92894
│  │  ├─ 22
│  │  │  ├─ 5562c339e766b9eed72fd911a8f2ad19bf4692
│  │  │  └─ d7fae80b1cb42e8668b0ff157888c893957765
│  │  ├─ 26
│  │  │  ├─ 762493228f9b88bd6c9462d362bba1844d0d97
│  │  │  └─ f3016b90b31501ba4bf0c5d1f4550e3341e11c
│  │  ├─ 27
│  │  │  └─ 352b2d7d2189056b6c256affce3f1392d55f75
│  │  ├─ 28
│  │  │  └─ 1cc7fa074aeeff5ed2daf579c6b05beacb88de
│  │  ├─ 2a
│  │  │  ├─ 02d4d104a5e8725ca001781f1caa70d9dcca1e
│  │  │  ├─ 453854999a2c81a10bebc896a701c90b113ddb
│  │  │  └─ f79436d936f78f7cb88e5ac7b7e4be13d25109
│  │  ├─ 2c
│  │  │  ├─ 2b2823f1d484f2faef34da2b1e0d2d3a93adff
│  │  │  └─ 7c5867b6a17262aad6c124a6e04c94373bc2ea
│  │  ├─ 2d
│  │  │  ├─ 9b9e75454fc6420bd4770cc0e340e86e68fb0a
│  │  │  └─ d77e4144168061330d1c7dcd89222f7d967067
│  │  ├─ 2f
│  │  │  └─ 71c98007dc93f824e182a91370753cafb7c187
│  │  ├─ 30
│  │  │  └─ a76f7854b2ef0862c3d0a232a0fb68e4a6ccb9
│  │  ├─ 31
│  │  │  └─ 95dc30ecc3a9793a2979156dbf4c7eeef4c0fb
│  │  ├─ 35
│  │  │  └─ a853fea50ca4c51d8a65dab69a8642f986b625
│  │  ├─ 3e
│  │  │  ├─ 135d41006a94bf43cd94f30f73f95bf8955e96
│  │  │  ├─ 287b930586de8ae01928b0079aa40485b4fc46
│  │  │  └─ fabf2a6b75fd54c45aa9aec77eb332e6cfe9dc
│  │  ├─ 41
│  │  │  └─ 508e8ceb69c2d3068c369f87a938f666ceed14
│  │  ├─ 42
│  │  │  └─ 4345088d2dd5478b8598d829763dccbc22a590
│  │  ├─ 43
│  │  │  └─ b40477dedd1615d09c1e125b584798cee9cd3c
│  │  ├─ 46
│  │  │  └─ 3b9c225d8e85aca047ac2ccea49add5e4ff67b
│  │  ├─ 47
│  │  │  └─ ca1bbbe5e275415436556ea4361653a0184ee7
│  │  ├─ 48
│  │  │  └─ f1813ba3b867452188d7c103ca9739ce8fa644
│  │  ├─ 4b
│  │  │  └─ 9ddc837d42755e4b21bfa1cc3218c2c56a61b1
│  │  ├─ 4c
│  │  │  └─ 599ba71a6afd8b888c8474f81cba310e39a088
│  │  ├─ 4d
│  │  │  └─ 427b9409a8cfd3f31692cdd500911aa9a81afa
│  │  ├─ 4e
│  │  │  ├─ 39720188911a4ded1170bf55011757440089e9
│  │  │  ├─ 876d203c698d6c499314e22f0ce64685939617
│  │  │  └─ d399e3fd6404e60be96a9f267f994640e9d1d5
│  │  ├─ 4f
│  │  │  └─ 5346aad077579dc90cd8a7f9dd445a33248929
│  │  ├─ 51
│  │  │  ├─ 104a6ee44c35f3b562978bba1d2c7dd508a27a
│  │  │  ├─ 5fd48fa99bdde47f1b9723eafa7cbe3c69c944
│  │  │  └─ b1a66ec24d869b9c147a6377472b2140228b5a
│  │  ├─ 53
│  │  │  └─ 11755304804cfcdf53e36c8c3e7d423986efff
│  │  ├─ 55
│  │  │  └─ 07dc28ee55f4088360b3699f19f6410e9429e7
│  │  ├─ 56
│  │  │  └─ d4eea7407eedda3e104edd4b69c216a1c94f45
│  │  ├─ 5a
│  │  │  └─ f9f60a4e53b96bef78f737e64e276af444c6d3
│  │  ├─ 5e
│  │  │  └─ accf80f6659d6206c2df5e541612b1e3f24e6c
│  │  ├─ 5f
│  │  │  ├─ 88d53f3f3a0885ea5c7dc7504aa0ffef0137b5
│  │  │  └─ f71d343ae997bc42fddd6402c840d04f6a2ff0
│  │  ├─ 60
│  │  │  └─ 621ec929469cf7f7ad5412e774d6c6f6779151
│  │  ├─ 62
│  │  │  └─ 5dd61d66c2670b5dc582b9277258284a35b30c
│  │  ├─ 63
│  │  │  ├─ 4e30739eecc5df912769ee441a97345586f261
│  │  │  └─ efcd2d62b5aaa4c46c8b5417407d068c0fb42d
│  │  ├─ 65
│  │  │  └─ 77cf2cb958d1a9391ab9b82525ece54810f6dd
│  │  ├─ 67
│  │  │  └─ 869595c571f55829dd3f7e15f262c0836b9a18
│  │  ├─ 6c
│  │  │  ├─ 4154df6e73ae24fec1f1350d32856245827ee2
│  │  │  └─ 7ba5dbf0a5f79e3920cc6ce161cf563d579bc4
│  │  ├─ 6d
│  │  │  └─ e461cffc731dcb688722f4e6bbe359d993a2b4
│  │  ├─ 6e
│  │  │  └─ 3462beb2d11706b0c947dc42c80d2beaec2f8e
│  │  ├─ 6f
│  │  │  └─ c39554ab26c01b9a5b26b5531ef8ea50354d15
│  │  ├─ 71
│  │  │  ├─ 70f8fe1c161417653afc3e666e536a191ed77a
│  │  │  └─ ea971fa25ed05ea65cff09465734beaa5d97d8
│  │  ├─ 72
│  │  │  └─ 132bd6c6c251a9cddf84ce81c1a50d88ed41a2
│  │  ├─ 74
│  │  │  ├─ 34d5c624ba0a97cfdfd68a6d273e77bdcea5cb
│  │  │  ├─ 56170fe82bbdae15819ca7f6fd15597e6db05d
│  │  │  └─ 80c278cddc55c175cfc680de9a00fbb4431528
│  │  ├─ 75
│  │  │  ├─ 9073c219491482111f7bd71e55b2645ecbcf08
│  │  │  └─ fc1e2cd8c17fa0bf29390712f0b59b2bd229ff
│  │  ├─ 7a
│  │  │  └─ 06761b43668808d40138f8f4500510cd313b07
│  │  ├─ 7b
│  │  │  ├─ 2b03428cbecb570c9d01f0c0ad4757b6f6752c
│  │  │  └─ db2d615058284195bbb353fceae0c332d4fcc6
│  │  ├─ 82
│  │  │  ├─ 00f1316c7d359019c30f29b2255c05bac3981f
│  │  │  └─ 238847580e9c220b9925633f5b8480bfb7810f
│  │  ├─ 83
│  │  │  ├─ 91227119b6a0550ef1c9f0ebb44b76cf593938
│  │  │  └─ ba9090ae18c1f930a6a6d1b4bcc002e14f931e
│  │  ├─ 84
│  │  │  └─ 64da131d5ab62049d809c7f5ab148caedc30c5
│  │  ├─ 85
│  │  │  └─ 9dd81b6175f611c7b6c8e0021fd681a0755f73
│  │  ├─ 87
│  │  │  └─ ce025a3485c18c977152e2ab101d51516a37dc
│  │  ├─ 89
│  │  │  └─ 3ac58bb0e15c50674111dc87673afb8e7d491f
│  │  ├─ 8a
│  │  │  └─ 3df0ab6a19f79639b467fc8a68e63a07837b0a
│  │  ├─ 8b
│  │  │  └─ cae89fb14f4dc04b4ee63d4761770eb5599571
│  │  ├─ 8e
│  │  │  └─ 88aca3a7bc789e96c8cfad43e47415badd21b4
│  │  ├─ 90
│  │  │  ├─ 07e975e9fee667ef6962939a69bbd236b28933
│  │  │  ├─ 23ed7cf8f52dc5b928ed576b2aaf211508322f
│  │  │  └─ 5af855a51e6853ca521a71cef82061226c844d
│  │  ├─ 91
│  │  │  └─ ba4d5d4f1215969aabcd37aa64fdbc14be15f0
│  │  ├─ 93
│  │  │  ├─ 59fbff3b829ab58ba46a3bf9a24b60356ad8f1
│  │  │  └─ 882420ec6b423a0da80ff2c029ac6f36677730
│  │  ├─ 95
│  │  │  ├─ b151c99a12a6a341ac5618b4829f6db3d95ac9
│  │  │  └─ cb04b8f1efde5f1d77ae202161744e612fdb47
│  │  ├─ 96
│  │  │  ├─ 6c899115f64bdce373735be212572fb3a7fe21
│  │  │  ├─ ae7250f306367b55791036e756ea26a2a2f981
│  │  │  └─ d85c0381e75a685c4d6535615697e06f58ae7f
│  │  ├─ 97
│  │  │  ├─ 5fb94185e4221598dacddbba3e44c4a547f6e6
│  │  │  └─ cded5014f6b32263abdf32968052d97527fa94
│  │  ├─ 98
│  │  │  └─ 45246b2e678e3c6cf195f60706363d15548b30
│  │  ├─ 9b
│  │  │  └─ 602785c4af6f72e2b50858e852f1c6eae5ebb8
│  │  ├─ 9d
│  │  │  └─ a0a8d32f0643b3ad6f3b31dd4da0d8be315425
│  │  ├─ 9e
│  │  │  └─ e019d21ead416199c8684deb96901f2e0edcf3
│  │  ├─ a2
│  │  │  ├─ 0b3f0da4079f666fc7cc5821ce222467ee553f
│  │  │  └─ 7c178f114c86ffdd306bc8a33474307eb4944b
│  │  ├─ a5
│  │  │  └─ f4b325d0f2b3294f5a9b6c233a36be8b19afd1
│  │  ├─ a6
│  │  │  └─ 83636fcd846dd9bc18de1d73eaabcb9e058aae
│  │  ├─ a8
│  │  │  └─ 6904487b2be3617d3f1445af8b1937e5fe6959
│  │  ├─ a9
│  │  │  └─ 85da5108f91982dbbecd786df3af0cdff88a61
│  │  ├─ aa
│  │  │  └─ 41a7dee219bbdfa4859ff676e907e80991a2ff
│  │  ├─ ad
│  │  │  └─ 304eba6aa34ce7cad6ef289c32064a977575e7
│  │  ├─ b2
│  │  │  └─ b979457b86b30f0c651d01ccfc36f385d2af85
│  │  ├─ ba
│  │  │  └─ 79248cc2217ae683cde79840b12e030d7b555a
│  │  ├─ bc
│  │  │  └─ d494daed8e548169e1a52e237cfbc06cc1ef13
│  │  ├─ bd
│  │  │  ├─ 08d5df944eb70fd8f29c289a9035f3aae8e906
│  │  │  └─ 8c564cf03ca2c4dec05bc33683b639a92e20ac
│  │  ├─ c3
│  │  │  ├─ 657f150922c322fe287a50289e7321eb195280
│  │  │  └─ aebde57ec497faec656effd34b65f34a6d912a
│  │  ├─ c6
│  │  │  └─ 36df04279b7a5f0fe04dcb9d1af2907b802728
│  │  ├─ c8
│  │  │  └─ 3cf0bae851a2b774c2164b8c6e1636675f532e
│  │  ├─ ca
│  │  │  └─ 8fa509156039cce3cfb8aa22c6ee1e736b883d
│  │  ├─ cb
│  │  │  └─ e97eabe1c394b0c5448d40eb0493952ad2fc14
│  │  ├─ cc
│  │  │  └─ d58269059858c0098d065b601e97e2222707bd
│  │  ├─ cd
│  │  │  ├─ 05fb088057d497ef01abe745c89e311a75833f
│  │  │  └─ 111dee9d42a0fc4a010032de65c08a829d3c01
│  │  ├─ cf
│  │  │  ├─ 550bb97f28e964daa4c3b4f933b224e4c55219
│  │  │  └─ bcc83bc7cde787a8129b27b62182c81d6cefe7
│  │  ├─ d1
│  │  │  ├─ 358d7a054d52aa0c50d65c9fa71937a2e02581
│  │  │  └─ 5077974583931a12d21916657dd8a30dc2f842
│  │  ├─ d2
│  │  │  └─ f1d6aabd655175b7cdb826a006bb55823baab2
│  │  ├─ d6
│  │  │  └─ 655652ddafbef4b2f224110de506734490d889
│  │  ├─ d7
│  │  │  └─ 9e86ff463ed48ae8079538ebb7deab763fa37d
│  │  ├─ d9
│  │  │  └─ 8edeeb6df29d818a35e2400517e5ae958461fe
│  │  ├─ da
│  │  │  ├─ 1d19bc377ea0478cbfb88b57421400db2c9111
│  │  │  └─ dae4a41811275038cadb08a1175ca1c6c50e2e
│  │  ├─ db
│  │  │  └─ cb0eb2dd55f1ae9565522f3d03e3889b60cad5
│  │  ├─ dc
│  │  │  └─ 94a1764588d775c6be8e04daee31cb9a930db3
│  │  ├─ dd
│  │  │  └─ 9d8f2bdbbd8e49cd169cbb4263411b328b7caa
│  │  ├─ de
│  │  │  ├─ 40e50cb737d2179625871b6b5e13845fa906cc
│  │  │  └─ e5eb82713f27108757a26fa033c091d06a9073
│  │  ├─ e0
│  │  │  └─ 0daa84d951ed10541d5b893cdb1ee2af7c6319
│  │  ├─ e1
│  │  │  └─ fde7d476ccb932f1832b63ffc2f092c84919f2
│  │  ├─ e3
│  │  │  └─ 34b666df5582b9f04650f8a818c43fc4bfc8b7
│  │  ├─ e7
│  │  │  └─ 26a7369c2994150f44da99ea9b6809190ffa40
│  │  ├─ ea
│  │  │  ├─ 47a526ba3724829aa38700a99aa84482a94893
│  │  │  └─ 9e8b8b18edf546b1a6ac818b7e7ab0a5edabb3
│  │  ├─ eb
│  │  │  └─ 913f310448681719463826c9afc919485d7298
│  │  ├─ ec
│  │  │  └─ fe55a05ecb3934097cee7ce2f7e4e21cd649b6
│  │  ├─ ee
│  │  │  ├─ 09f665141bf46e3b731e02976f9c3d1743c95b
│  │  │  └─ 2305632a46108ddcd6a17454516310d2f72ebe
│  │  ├─ ef
│  │  │  └─ 667e950c5ae4d2312aaa9f2ab4f9277c56d7e5
│  │  ├─ f0
│  │  │  └─ 4ac753f8162cf2a4b64455d1408a5dc0044799
│  │  ├─ f2
│  │  │  └─ ce760880af094142246fea6d2862f306b648ad
│  │  ├─ f4
│  │  │  └─ 993fb9f6a97d5a1fa75eb5a614a9ed1b7340da
│  │  ├─ f5
│  │  │  ├─ 5ce860062701182356398b4eb83814262fa074
│  │  │  └─ f3e62d43a357575102edbaf1514511df1ca22a
│  │  ├─ f7
│  │  │  └─ e11f837a65c0714fb5be5ec8c2914b5d05f7b4
│  │  ├─ fb
│  │  │  └─ e2a6dc2c172185e19fadc3d0ad0e5522254844
│  │  ├─ fc
│  │  │  └─ 1e6946e7b61e09fe180b8742c54db30f2db4ce
│  │  ├─ ff
│  │  │  └─ 9a143067481037f3eb3b0a4f18be7b8676e58c
│  │  ├─ info
│  │  └─ pack
│  │     ├─ pack-44cdc02b7f68f346b1f0a4186c62b5b576e6c1e6.idx
│  │     ├─ pack-44cdc02b7f68f346b1f0a4186c62b5b576e6c1e6.pack
│  │     └─ pack-44cdc02b7f68f346b1f0a4186c62b5b576e6c1e6.rev
│  ├─ ORIG_HEAD
│  ├─ packed-refs
│  └─ refs
│     ├─ heads
│     │  ├─ fate
│     │  │  └─ rag
│     │  └─ master
│     ├─ remotes
│     │  └─ origin
│     │     ├─ fate
│     │     │  └─ rag
│     │     ├─ HEAD
│     │     └─ master
│     ├─ stash
│     └─ tags
├─ .gitignore
├─ .husky
│  └─ pre-commit
├─ .vscode
│  └─ settings.json
├─ app
│  ├─ (commonLayout)
│  │  ├─ app
│  │  │  └─ (appDetailLayout)
│  │  │     ├─ layout.tsx
│  │  │     └─ [appId]
│  │  │        ├─ annotations
│  │  │        │  └─ page.tsx
│  │  │        ├─ configuration
│  │  │        │  └─ page.tsx
│  │  │        ├─ develop
│  │  │        │  └─ page.tsx
│  │  │        ├─ layout.tsx
│  │  │        ├─ logs
│  │  │        │  └─ page.tsx
│  │  │        ├─ overview
│  │  │        │  ├─ cardView.tsx
│  │  │        │  ├─ chartView.tsx
│  │  │        │  ├─ page.tsx
│  │  │        │  └─ tracing
│  │  │        │     ├─ config-button.tsx
│  │  │        │     ├─ config-popup.tsx
│  │  │        │     ├─ config.ts
│  │  │        │     ├─ field.tsx
│  │  │        │     ├─ panel.tsx
│  │  │        │     ├─ provider-config-modal.tsx
│  │  │        │     ├─ provider-panel.tsx
│  │  │        │     ├─ toggle-fold-btn.tsx
│  │  │        │     ├─ tracing-icon.tsx
│  │  │        │     └─ type.ts
│  │  │        ├─ style.module.css
│  │  │        └─ workflow
│  │  │           └─ page.tsx
│  │  ├─ apps
│  │  │  ├─ AppCard.tsx
│  │  │  ├─ Apps.tsx
│  │  │  ├─ assets
│  │  │  │  ├─ add.svg
│  │  │  │  ├─ chat-solid.svg
│  │  │  │  ├─ chat.svg
│  │  │  │  ├─ completion-solid.svg
│  │  │  │  ├─ completion.svg
│  │  │  │  ├─ discord.svg
│  │  │  │  ├─ github.svg
│  │  │  │  ├─ image
│  │  │  │  │  ├─ add.png
│  │  │  │  │  ├─ back.png
│  │  │  │  │  ├─ bannerMap.png
│  │  │  │  │  ├─ circleIcon.png
│  │  │  │  │  ├─ editIcon.png
│  │  │  │  │  ├─ iconBook.png
│  │  │  │  │  ├─ rightGo.png
│  │  │  │  │  ├─ setEdit.png
│  │  │  │  │  └─ user.png
│  │  │  │  ├─ link-gray.svg
│  │  │  │  ├─ link.svg
│  │  │  │  └─ right-arrow.svg
│  │  │  ├─ component
│  │  │  │  ├─ agentChatPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ allPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ areaPage
│  │  │  │  │  ├─ addArea.tsx
│  │  │  │  │  ├─ areaEdit.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ base
│  │  │  │  │  ├─ addModal.tsx
│  │  │  │  │  ├─ baseCard.tsx
│  │  │  │  │  ├─ baseStyle.module.scss
│  │  │  │  │  ├─ typeCard.tsx
│  │  │  │  │  └─ userCard.tsx
│  │  │  │  ├─ chatPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ dcoosPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ dcoosSignPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ metabolicPage
│  │  │  │  │  └─ index.tsx
│  │  │  │  └─ workflowPage
│  │  │  │     └─ index.tsx
│  │  │  ├─ hooks
│  │  │  │  └─ useAppsQueryState.ts
│  │  │  ├─ NewAppCard.tsx
│  │  │  ├─ page.tsx
│  │  │  ├─ style.module.css
│  │  │  └─ _document.tsx
│  │  ├─ datasets
│  │  │  ├─ (datasetDetailLayout)
│  │  │  │  ├─ layout.tsx
│  │  │  │  └─ [datasetId]
│  │  │  │     ├─ api
│  │  │  │     │  └─ page.tsx
│  │  │  │     ├─ documents
│  │  │  │     │  ├─ create
│  │  │  │     │  │  └─ page.tsx
│  │  │  │     │  ├─ page.tsx
│  │  │  │     │  ├─ style.module.css
│  │  │  │     │  └─ [documentId]
│  │  │  │     │     ├─ page.tsx
│  │  │  │     │     └─ settings
│  │  │  │     │        └─ page.tsx
│  │  │  │     ├─ hitTesting
│  │  │  │     │  └─ page.tsx
│  │  │  │     ├─ layout.tsx
│  │  │  │     ├─ settings
│  │  │  │     │  └─ page.tsx
│  │  │  │     └─ style.module.css
│  │  │  ├─ ApiServer.tsx
│  │  │  ├─ Container.tsx
│  │  │  ├─ create
│  │  │  │  └─ page.tsx
│  │  │  ├─ DatasetCard.tsx
│  │  │  ├─ DatasetFooter.tsx
│  │  │  ├─ Datasets.tsx
│  │  │  ├─ Doc.tsx
│  │  │  ├─ NewDatasetCard.tsx
│  │  │  ├─ page.tsx
│  │  │  └─ template
│  │  │     ├─ template.en.mdx
│  │  │     └─ template.zh.mdx
│  │  ├─ explore
│  │  │  ├─ apps
│  │  │  │  └─ page.tsx
│  │  │  ├─ installed
│  │  │  │  └─ [appId]
│  │  │  │     └─ page.tsx
│  │  │  └─ layout.tsx
│  │  ├─ layout.tsx
│  │  ├─ list.module.css
│  │  └─ tools
│  │     ├─ createByCode
│  │     │  └─ page.tsx
│  │     ├─ createByUrl
│  │     │  ├─ page.tsx
│  │     │  └─ paramsUtils.tsx
│  │     ├─ page.tsx
│  │     └─ tool.module.css
│  ├─ (shareLayout)
│  │  ├─ chat
│  │  │  └─ [token]
│  │  │     └─ page.tsx
│  │  ├─ chatbot
│  │  │  └─ [token]
│  │  │     └─ page.tsx
│  │  ├─ completion
│  │  │  └─ [token]
│  │  │     └─ page.tsx
│  │  ├─ layout.tsx
│  │  ├─ webapp-signin
│  │  │  └─ page.tsx
│  │  └─ workflow
│  │     └─ [token]
│  │        └─ page.tsx
│  ├─ activate
│  │  ├─ activateForm.tsx
│  │  ├─ page.tsx
│  │  ├─ style.module.css
│  │  └─ team-28x28.png
│  ├─ components
│  │  ├─ app
│  │  │  ├─ annotation
│  │  │  │  ├─ add-annotation-modal
│  │  │  │  │  ├─ edit-item
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ batch-add-annotation-modal
│  │  │  │  │  ├─ csv-downloader.tsx
│  │  │  │  │  ├─ csv-uploader.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ edit-annotation-modal
│  │  │  │  │  ├─ edit-item
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ empty-element.tsx
│  │  │  │  ├─ filter.tsx
│  │  │  │  ├─ header-opts
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ list.tsx
│  │  │  │  ├─ remove-annotation-confirm-modal
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  ├─ type.ts
│  │  │  │  └─ view-annotation-modal
│  │  │  │     ├─ hit-history-no-data.tsx
│  │  │  │     ├─ index.tsx
│  │  │  │     └─ style.module.css
│  │  │  ├─ app-publisher
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ publish-with-multiple-model.tsx
│  │  │  │  └─ suggested-action.tsx
│  │  │  ├─ configuration
│  │  │  │  ├─ base
│  │  │  │  │  ├─ feature-panel
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ group-name
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ icons
│  │  │  │  │  │  ├─ citation.tsx
│  │  │  │  │  │  ├─ more-like-this-icon.tsx
│  │  │  │  │  │  ├─ remove-icon
│  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  │  └─ suggested-questions-after-answer-icon.tsx
│  │  │  │  │  ├─ operation-btn
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ var-highlight
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  └─ warning-mask
│  │  │  │  │     ├─ cannot-query-dataset.tsx
│  │  │  │  │     ├─ formatting-changed.tsx
│  │  │  │  │     ├─ has-not-set-api.tsx
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     └─ style.module.css
│  │  │  │  ├─ config
│  │  │  │  │  ├─ agent
│  │  │  │  │  │  ├─ agent-setting
│  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  └─ item-panel.tsx
│  │  │  │  │  │  ├─ agent-tools
│  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  └─ setting-built-in-tool.tsx
│  │  │  │  │  │  └─ prompt-editor.tsx
│  │  │  │  │  ├─ agent-setting-button.tsx
│  │  │  │  │  ├─ assistant-type-picker
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ automatic
│  │  │  │  │  │  ├─ automatic-btn.tsx
│  │  │  │  │  │  └─ get-automatic-res.tsx
│  │  │  │  │  ├─ feature
│  │  │  │  │  │  ├─ add-feature-btn
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  ├─ choose-feature
│  │  │  │  │  │  │  ├─ feature-item
│  │  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  │  ├─ preview-imgs
│  │  │  │  │  │  │  │  │  ├─ citation.png
│  │  │  │  │  │  │  │  │  ├─ citation.svg
│  │  │  │  │  │  │  │  │  ├─ citations-and-attributions-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ conversation-opener-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ more-like-this-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ more-like-this.png
│  │  │  │  │  │  │  │  │  ├─ more-like-this.svg
│  │  │  │  │  │  │  │  │  ├─ next-question-suggestion-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ opening-statement.png
│  │  │  │  │  │  │  │  │  ├─ opening-suggestion-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ speech-to-text-preview@2x.png
│  │  │  │  │  │  │  │  │  ├─ speech-to-text.png
│  │  │  │  │  │  │  │  │  ├─ speech-to-text.svg
│  │  │  │  │  │  │  │  │  ├─ suggested-questions-after-answer.png
│  │  │  │  │  │  │  │  │  ├─ suggested-questions-after-answer.svg
│  │  │  │  │  │  │  │  │  ├─ text-to-audio-preview-assistant@2x.png
│  │  │  │  │  │  │  │  │  └─ text-to-audio-preview-completion@2x.png
│  │  │  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  ├─ feature-group
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  └─ use-feature.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ config-prompt
│  │  │  │  │  ├─ advanced-prompt-input.tsx
│  │  │  │  │  ├─ confirm-add-var
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ conversation-histroy
│  │  │  │  │  │  ├─ edit-modal.tsx
│  │  │  │  │  │  └─ history-panel.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ message-type-selector.tsx
│  │  │  │  │  ├─ prompt-editor-height-resize-wrap.tsx
│  │  │  │  │  ├─ simple-prompt-input.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ config-var
│  │  │  │  │  ├─ config-modal
│  │  │  │  │  │  ├─ field.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ config-select
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ config-string
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ input-type-icon.tsx
│  │  │  │  │  ├─ modal-foot.tsx
│  │  │  │  │  ├─ select-type-item
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ select-var-type.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ config-vision
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ param-config-content.tsx
│  │  │  │  │  ├─ param-config.tsx
│  │  │  │  │  └─ radio-group
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     └─ style.module.css
│  │  │  │  ├─ config-voice
│  │  │  │  │  ├─ param-config-content.tsx
│  │  │  │  │  └─ param-config.tsx
│  │  │  │  ├─ ctrl-btn-group
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ dataset-config
│  │  │  │  │  ├─ card-item
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ item.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ context-var
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ style.module.css
│  │  │  │  │  │  └─ var-picker.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ params-config
│  │  │  │  │  │  ├─ config-content.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ select-dataset
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ settings-modal
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ type-icon
│  │  │  │  │     └─ index.tsx
│  │  │  │  ├─ debug
│  │  │  │  │  ├─ debug-with-multiple-model
│  │  │  │  │  │  ├─ chat-item.tsx
│  │  │  │  │  │  ├─ context.tsx
│  │  │  │  │  │  ├─ debug-item.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ model-parameter-trigger.tsx
│  │  │  │  │  │  └─ text-generation-item.tsx
│  │  │  │  │  ├─ debug-with-single-model
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ hooks.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ types.ts
│  │  │  │  ├─ features
│  │  │  │  │  ├─ chat-group
│  │  │  │  │  │  ├─ citation
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ opening-statement
│  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  │  ├─ speech-to-text
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  ├─ suggested-questions-after-answer
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  └─ text-to-speech
│  │  │  │  │  │     └─ index.tsx
│  │  │  │  │  └─ experience-enchance-group
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     └─ more-like-this
│  │  │  │  │        └─ index.tsx
│  │  │  │  ├─ hooks
│  │  │  │  │  └─ use-advanced-prompt-config.ts
│  │  │  │  ├─ images
│  │  │  │  │  └─ prompt.svg
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ prompt-mode
│  │  │  │  │  └─ advanced-mode-waring.tsx
│  │  │  │  ├─ prompt-value-panel
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  ├─ toolbox
│  │  │  │  │  ├─ annotation
│  │  │  │  │  │  ├─ annotation-ctrl-btn
│  │  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  │  ├─ config-param-modal.tsx
│  │  │  │  │  │  ├─ config-param.tsx
│  │  │  │  │  │  ├─ type.ts
│  │  │  │  │  │  └─ use-annotation-config.ts
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ moderation
│  │  │  │  │  │  ├─ form-generation.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ moderation-content.tsx
│  │  │  │  │  │  └─ moderation-setting-modal.tsx
│  │  │  │  │  └─ score-slider
│  │  │  │  │     ├─ base-slider
│  │  │  │  │     │  ├─ index.tsx
│  │  │  │  │     │  └─ style.module.css
│  │  │  │  │     └─ index.tsx
│  │  │  │  └─ tools
│  │  │  │     ├─ external-data-tool-modal.tsx
│  │  │  │     └─ index.tsx
│  │  │  ├─ create-app-dialog
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ newAppDialog.tsx
│  │  │  ├─ create-app-modal
│  │  │  │  ├─ advanced.png
│  │  │  │  ├─ basic.png
│  │  │  │  ├─ grid-bg-agent-chat.svg
│  │  │  │  ├─ grid-bg-chat.svg
│  │  │  │  ├─ grid-bg-completion.svg
│  │  │  │  ├─ grid-bg-workflow.svg
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ create-from-dsl-modal
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ uploader.tsx
│  │  │  ├─ duplicate-modal
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ log
│  │  │  │  ├─ filter.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ list.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  └─ var-panel.tsx
│  │  │  ├─ log-annotation
│  │  │  │  └─ index.tsx
│  │  │  ├─ overview
│  │  │  │  ├─ apikey-info-panel
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ progress
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     └─ style.module.css
│  │  │  │  ├─ appCard.tsx
│  │  │  │  ├─ appChart.tsx
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ chromeplugin-install.svg
│  │  │  │  │  ├─ chromeplugin-option.svg
│  │  │  │  │  ├─ code-browser.svg
│  │  │  │  │  ├─ iframe-option.svg
│  │  │  │  │  ├─ refresh-hover.svg
│  │  │  │  │  ├─ refresh.svg
│  │  │  │  │  └─ scripts-option.svg
│  │  │  │  ├─ customize
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ embedded
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ settings
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  └─ style.module.css
│  │  │  ├─ store.ts
│  │  │  ├─ switch-app-modal
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ text-generate
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ item
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ result-tab.tsx
│  │  │  │  └─ saved-items
│  │  │  │     ├─ index.tsx
│  │  │  │     └─ no-data
│  │  │  │        └─ index.tsx
│  │  │  ├─ type-selector
│  │  │  │  └─ index.tsx
│  │  │  └─ workflow-log
│  │  │     ├─ detail.tsx
│  │  │     ├─ filter.tsx
│  │  │     ├─ index.tsx
│  │  │     ├─ list.tsx
│  │  │     └─ style.module.css
│  │  ├─ app-sidebar
│  │  │  ├─ app-info.tsx
│  │  │  ├─ basic.tsx
│  │  │  ├─ completion.png
│  │  │  ├─ expert.png
│  │  │  ├─ index.tsx
│  │  │  ├─ navLink.tsx
│  │  │  └─ style.module.css
│  │  ├─ base
│  │  │  ├─ agent-log-modal
│  │  │  │  ├─ detail.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ iteration.tsx
│  │  │  │  ├─ result.tsx
│  │  │  │  ├─ tool-call.tsx
│  │  │  │  └─ tracing.tsx
│  │  │  ├─ app-icon
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ app-unavailable.tsx
│  │  │  ├─ audio-btn
│  │  │  │  ├─ audio.player.manager.ts
│  │  │  │  ├─ audio.ts
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ auto-height-textarea
│  │  │  │  ├─ common.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.scss
│  │  │  ├─ avatar
│  │  │  │  └─ index.tsx
│  │  │  ├─ block-input
│  │  │  │  └─ index.tsx
│  │  │  ├─ button
│  │  │  │  ├─ add-button.tsx
│  │  │  │  ├─ index.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ chat
│  │  │  │  ├─ chat
│  │  │  │  │  ├─ answer
│  │  │  │  │  │  ├─ agent-content.tsx
│  │  │  │  │  │  ├─ basic-content.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ more.tsx
│  │  │  │  │  │  ├─ operation.tsx
│  │  │  │  │  │  ├─ suggested-questions.tsx
│  │  │  │  │  │  └─ workflow-process.tsx
│  │  │  │  │  ├─ chat-input.tsx
│  │  │  │  │  ├─ citation
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ popup.tsx
│  │  │  │  │  │  ├─ progress-tooltip.tsx
│  │  │  │  │  │  └─ tooltip.tsx
│  │  │  │  │  ├─ context.tsx
│  │  │  │  │  ├─ hooks.ts
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ loading-anim
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ log
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ question.tsx
│  │  │  │  │  ├─ thought
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ panel.tsx
│  │  │  │  │  │  └─ tool.tsx
│  │  │  │  │  ├─ try-to-ask.tsx
│  │  │  │  │  └─ type.ts
│  │  │  │  ├─ chat-with-history
│  │  │  │  │  ├─ chat-wrapper.tsx
│  │  │  │  │  ├─ config-panel
│  │  │  │  │  │  ├─ form-input.tsx
│  │  │  │  │  │  ├─ form.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ context.tsx
│  │  │  │  │  ├─ header-in-mobile.tsx
│  │  │  │  │  ├─ header.tsx
│  │  │  │  │  ├─ hooks.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ sidebar
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     ├─ item.tsx
│  │  │  │  │     ├─ list.tsx
│  │  │  │  │     └─ rename-modal.tsx
│  │  │  │  ├─ constants.ts
│  │  │  │  ├─ embedded-chatbot
│  │  │  │  │  ├─ chat-wrapper.tsx
│  │  │  │  │  ├─ config-panel
│  │  │  │  │  │  ├─ form-input.tsx
│  │  │  │  │  │  ├─ form.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ context.tsx
│  │  │  │  │  ├─ header.tsx
│  │  │  │  │  ├─ hooks.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ theme
│  │  │  │  │  │  ├─ theme-context.ts
│  │  │  │  │  │  └─ utils.ts
│  │  │  │  │  └─ utils.ts
│  │  │  │  └─ types.ts
│  │  │  ├─ checkbox
│  │  │  │  ├─ assets
│  │  │  │  │  └─ check.svg
│  │  │  │  ├─ index.module.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ confirm
│  │  │  │  ├─ common.module.css
│  │  │  │  ├─ common.tsx
│  │  │  │  └─ index.tsx
│  │  │  ├─ confirm-ui
│  │  │  │  └─ index.tsx
│  │  │  ├─ copy-btn
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ copy-feedback
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ copy-icon
│  │  │  │  └─ index.tsx
│  │  │  ├─ custom-icon
│  │  │  │  └─ index.tsx
│  │  │  ├─ dialog
│  │  │  │  └─ index.tsx
│  │  │  ├─ divider
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ drawer
│  │  │  │  └─ index.tsx
│  │  │  ├─ drawer-plus
│  │  │  │  └─ index.tsx
│  │  │  ├─ dropdown
│  │  │  │  └─ index.tsx
│  │  │  ├─ emoji-picker
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ features
│  │  │  │  ├─ context.tsx
│  │  │  │  ├─ feature-choose
│  │  │  │  │  ├─ feature-group
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ feature-item
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ preview-imgs
│  │  │  │  │  │  │  ├─ citation.svg
│  │  │  │  │  │  │  ├─ citations-and-attributions-preview@2x.png
│  │  │  │  │  │  │  ├─ conversation-opener-preview@2x.png
│  │  │  │  │  │  │  ├─ more-like-this-preview@2x.png
│  │  │  │  │  │  │  ├─ more-like-this.svg
│  │  │  │  │  │  │  ├─ next-question-suggestion-preview@2x.png
│  │  │  │  │  │  │  ├─ opening-statement.png
│  │  │  │  │  │  │  ├─ opening-suggestion-preview@2x.png
│  │  │  │  │  │  │  ├─ speech-to-text-preview@2x.png
│  │  │  │  │  │  │  ├─ speech-to-text.svg
│  │  │  │  │  │  │  ├─ suggested-questions-after-answer.svg
│  │  │  │  │  │  │  ├─ text-to-audio-preview-assistant@2x.png
│  │  │  │  │  │  │  └─ text-to-audio-preview-completion@2x.png
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ feature-modal.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ feature-panel
│  │  │  │  │  ├─ citation
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ file-upload
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ param-config-content.tsx
│  │  │  │  │  │  ├─ param-config.tsx
│  │  │  │  │  │  └─ radio-group
│  │  │  │  │  │     ├─ index.tsx
│  │  │  │  │  │     └─ style.module.css
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ moderation
│  │  │  │  │  │  ├─ form-generation.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ moderation-content.tsx
│  │  │  │  │  │  └─ moderation-setting-modal.tsx
│  │  │  │  │  ├─ opening-statement
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ score-slider
│  │  │  │  │  │  ├─ base-slider
│  │  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ speech-to-text
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ suggested-questions-after-answer
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ text-to-speech
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     ├─ param-config-content.tsx
│  │  │  │  │     └─ params-config.tsx
│  │  │  │  ├─ hooks.ts
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ store.ts
│  │  │  │  └─ types.ts
│  │  │  ├─ file-icon
│  │  │  │  └─ index.tsx
│  │  │  ├─ float-popover-container
│  │  │  │  └─ index.tsx
│  │  │  ├─ float-right-container
│  │  │  │  └─ index.tsx
│  │  │  ├─ ga
│  │  │  │  └─ index.tsx
│  │  │  ├─ grid-mask
│  │  │  │  └─ index.tsx
│  │  │  ├─ icons
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ image
│  │  │  │  │  │  └─ llm
│  │  │  │  │  │     ├─ baichuan-text-cn.png
│  │  │  │  │  │     ├─ minimax-text.png
│  │  │  │  │  │     ├─ minimax.png
│  │  │  │  │  │     ├─ tongyi-text-cn.png
│  │  │  │  │  │     ├─ tongyi-text.png
│  │  │  │  │  │     ├─ tongyi.png
│  │  │  │  │  │     ├─ wxyy-text-cn.png
│  │  │  │  │  │     ├─ wxyy-text.png
│  │  │  │  │  │     └─ wxyy.png
│  │  │  │  │  ├─ public
│  │  │  │  │  │  ├─ avatar
│  │  │  │  │  │  │  ├─ robot.svg
│  │  │  │  │  │  │  └─ user.svg
│  │  │  │  │  │  ├─ billing
│  │  │  │  │  │  │  └─ sparkles.svg
│  │  │  │  │  │  ├─ common
│  │  │  │  │  │  │  ├─ d.svg
│  │  │  │  │  │  │  ├─ diagonal-dividing-line.svg
│  │  │  │  │  │  │  ├─ dify.svg
│  │  │  │  │  │  │  ├─ github.svg
│  │  │  │  │  │  │  ├─ line-3.svg
│  │  │  │  │  │  │  ├─ message-chat-square.svg
│  │  │  │  │  │  │  ├─ multi-path-retrieval.svg
│  │  │  │  │  │  │  ├─ n-to-1-retrieval.svg
│  │  │  │  │  │  │  └─ notion.svg
│  │  │  │  │  │  ├─ files
│  │  │  │  │  │  │  ├─ csv.svg
│  │  │  │  │  │  │  ├─ doc.svg
│  │  │  │  │  │  │  ├─ docx.svg
│  │  │  │  │  │  │  ├─ html.svg
│  │  │  │  │  │  │  ├─ json.svg
│  │  │  │  │  │  │  ├─ md.svg
│  │  │  │  │  │  │  ├─ pdf.svg
│  │  │  │  │  │  │  ├─ txt.svg
│  │  │  │  │  │  │  ├─ unknow.svg
│  │  │  │  │  │  │  ├─ xlsx.svg
│  │  │  │  │  │  │  └─ yaml.svg
│  │  │  │  │  │  ├─ llm
│  │  │  │  │  │  │  ├─ anthropic-text.svg
│  │  │  │  │  │  │  ├─ anthropic.svg
│  │  │  │  │  │  │  ├─ azure-openai-service-text.svg
│  │  │  │  │  │  │  ├─ azure-openai-service.svg
│  │  │  │  │  │  │  ├─ azureai-text.svg
│  │  │  │  │  │  │  ├─ azureai.svg
│  │  │  │  │  │  │  ├─ baichuan-text.svg
│  │  │  │  │  │  │  ├─ baichuan.svg
│  │  │  │  │  │  │  ├─ chatglm-text.svg
│  │  │  │  │  │  │  ├─ chatglm.svg
│  │  │  │  │  │  │  ├─ cohere-text.svg
│  │  │  │  │  │  │  ├─ cohere.svg
│  │  │  │  │  │  │  ├─ gpt-3.svg
│  │  │  │  │  │  │  ├─ gpt-4.svg
│  │  │  │  │  │  │  ├─ huggingface-text-hub.svg
│  │  │  │  │  │  │  ├─ huggingface-text.svg
│  │  │  │  │  │  │  ├─ huggingface.svg
│  │  │  │  │  │  │  ├─ iflytek-spark-text-cn.svg
│  │  │  │  │  │  │  ├─ iflytek-spark-text.svg
│  │  │  │  │  │  │  ├─ iflytek-spark.svg
│  │  │  │  │  │  │  ├─ jina-text.svg
│  │  │  │  │  │  │  ├─ jina.svg
│  │  │  │  │  │  │  ├─ localai-text.svg
│  │  │  │  │  │  │  ├─ localai.svg
│  │  │  │  │  │  │  ├─ microsoft.svg
│  │  │  │  │  │  │  ├─ openai-black.svg
│  │  │  │  │  │  │  ├─ openai-blue.svg
│  │  │  │  │  │  │  ├─ openai-green.svg
│  │  │  │  │  │  │  ├─ openai-text.svg
│  │  │  │  │  │  │  ├─ openai-transparent.svg
│  │  │  │  │  │  │  ├─ openai-violet.svg
│  │  │  │  │  │  │  ├─ openllm-text.svg
│  │  │  │  │  │  │  ├─ openllm.svg
│  │  │  │  │  │  │  ├─ replicate-text.svg
│  │  │  │  │  │  │  ├─ replicate.svg
│  │  │  │  │  │  │  ├─ xorbits-inference-text.svg
│  │  │  │  │  │  │  ├─ xorbits-inference.svg
│  │  │  │  │  │  │  ├─ zhipuai-text-cn.svg
│  │  │  │  │  │  │  ├─ zhipuai-text.svg
│  │  │  │  │  │  │  └─ zhipuai.svg
│  │  │  │  │  │  ├─ model
│  │  │  │  │  │  │  └─ checked.svg
│  │  │  │  │  │  ├─ other
│  │  │  │  │  │  │  ├─ default-tool-icon.svg
│  │  │  │  │  │  │  ├─ Icon-3-dots.svg
│  │  │  │  │  │  │  └─ row-struct.svg
│  │  │  │  │  │  ├─ plugins
│  │  │  │  │  │  │  ├─ google.svg
│  │  │  │  │  │  │  ├─ web-reader.svg
│  │  │  │  │  │  │  └─ wikipedia.svg
│  │  │  │  │  │  ├─ thought
│  │  │  │  │  │  │  ├─ data-set.svg
│  │  │  │  │  │  │  ├─ loading.svg
│  │  │  │  │  │  │  ├─ search.svg
│  │  │  │  │  │  │  ├─ thought-list.svg
│  │  │  │  │  │  │  └─ web-reader.svg
│  │  │  │  │  │  └─ tracing
│  │  │  │  │  │     ├─ langfuse-icon-big.svg
│  │  │  │  │  │     ├─ langfuse-icon.svg
│  │  │  │  │  │     ├─ langsmith-icon-big.svg
│  │  │  │  │  │     ├─ langsmith-icon.svg
│  │  │  │  │  │     └─ tracing-icon.svg
│  │  │  │  │  └─ vender
│  │  │  │  │     ├─ line
│  │  │  │  │     │  ├─ alertsAndFeedback
│  │  │  │  │     │  │  ├─ alert-triangle.svg
│  │  │  │  │     │  │  ├─ thumbs-down.svg
│  │  │  │  │     │  │  └─ thumbs-up.svg
│  │  │  │  │     │  ├─ arrows
│  │  │  │  │     │  │  ├─ arrow-narrow-left.svg
│  │  │  │  │     │  │  ├─ arrow-up-right.svg
│  │  │  │  │     │  │  ├─ chevron-down-double.svg
│  │  │  │  │     │  │  ├─ chevron-right.svg
│  │  │  │  │     │  │  ├─ chevron-selector-vertical.svg
│  │  │  │  │     │  │  ├─ refresh-ccw-01.svg
│  │  │  │  │     │  │  ├─ refresh-cw-05.svg
│  │  │  │  │     │  │  └─ reverse-left.svg
│  │  │  │  │     │  ├─ communication
│  │  │  │  │     │  │  ├─ ai-text.svg
│  │  │  │  │     │  │  ├─ chat-bot-slim.svg
│  │  │  │  │     │  │  ├─ chat-bot.svg
│  │  │  │  │     │  │  ├─ cute-robot.svg
│  │  │  │  │     │  │  ├─ message-check-remove.svg
│  │  │  │  │     │  │  └─ message-fast-plus.svg
│  │  │  │  │     │  ├─ development
│  │  │  │  │     │  │  ├─ artificial-brain.svg
│  │  │  │  │     │  │  ├─ bar-chart-square-02.svg
│  │  │  │  │     │  │  ├─ brackets-x.svg
│  │  │  │  │     │  │  ├─ code-browser.svg
│  │  │  │  │     │  │  ├─ container.svg
│  │  │  │  │     │  │  ├─ database-01.svg
│  │  │  │  │     │  │  ├─ database-03.svg
│  │  │  │  │     │  │  ├─ file-heart-02.svg
│  │  │  │  │     │  │  ├─ git-branch-01.svg
│  │  │  │  │     │  │  ├─ prompt-engineering.svg
│  │  │  │  │     │  │  ├─ puzzle-piece-01.svg
│  │  │  │  │     │  │  ├─ terminal-square.svg
│  │  │  │  │     │  │  ├─ variable.svg
│  │  │  │  │     │  │  └─ webhooks.svg
│  │  │  │  │     │  ├─ editor
│  │  │  │  │     │  │  ├─ align-left.svg
│  │  │  │  │     │  │  ├─ bezier-curve-03.svg
│  │  │  │  │     │  │  ├─ colors.svg
│  │  │  │  │     │  │  ├─ image-indent-left.svg
│  │  │  │  │     │  │  ├─ left-indent-02.svg
│  │  │  │  │     │  │  ├─ letter-spacing-01.svg
│  │  │  │  │     │  │  └─ type-square.svg
│  │  │  │  │     │  ├─ education
│  │  │  │  │     │  │  └─ book-open-01.svg
│  │  │  │  │     │  ├─ files
│  │  │  │  │     │  │  ├─ clipboard-check.svg
│  │  │  │  │     │  │  ├─ clipboard.svg
│  │  │  │  │     │  │  ├─ file-02.svg
│  │  │  │  │     │  │  ├─ file-arrow-01.svg
│  │  │  │  │     │  │  ├─ file-check-02.svg
│  │  │  │  │     │  │  ├─ file-download-02.svg
│  │  │  │  │     │  │  ├─ file-plus-01.svg
│  │  │  │  │     │  │  ├─ file-plus-02.svg
│  │  │  │  │     │  │  ├─ file-text.svg
│  │  │  │  │     │  │  ├─ file-upload.svg
│  │  │  │  │     │  │  └─ folder.svg
│  │  │  │  │     │  ├─ financeAndECommerce
│  │  │  │  │     │  │  ├─ balance.svg
│  │  │  │  │     │  │  ├─ coins-stacked-01.svg
│  │  │  │  │     │  │  ├─ gold-coin.svg
│  │  │  │  │     │  │  ├─ receipt-list.svg
│  │  │  │  │     │  │  ├─ tag-01.svg
│  │  │  │  │     │  │  └─ tag-03.svg
│  │  │  │  │     │  ├─ general
│  │  │  │  │     │  │  ├─ at-sign.svg
│  │  │  │  │     │  │  ├─ bookmark.svg
│  │  │  │  │     │  │  ├─ check-done-01.svg
│  │  │  │  │     │  │  ├─ check.svg
│  │  │  │  │     │  │  ├─ checklist-square.svg
│  │  │  │  │     │  │  ├─ dots-grid.svg
│  │  │  │  │     │  │  ├─ edit-02.svg
│  │  │  │  │     │  │  ├─ edit-04.svg
│  │  │  │  │     │  │  ├─ edit-05.svg
│  │  │  │  │     │  │  ├─ hash-02.svg
│  │  │  │  │     │  │  ├─ info-circle.svg
│  │  │  │  │     │  │  ├─ link-03.svg
│  │  │  │  │     │  │  ├─ link-external-02.svg
│  │  │  │  │     │  │  ├─ log-in-04.svg
│  │  │  │  │     │  │  ├─ log-out-01.svg
│  │  │  │  │     │  │  ├─ log-out-04.svg
│  │  │  │  │     │  │  ├─ menu-01.svg
│  │  │  │  │     │  │  ├─ pin-01.svg
│  │  │  │  │     │  │  ├─ pin-02.svg
│  │  │  │  │     │  │  ├─ plus-02.svg
│  │  │  │  │     │  │  ├─ settings-01.svg
│  │  │  │  │     │  │  ├─ settings-04.svg
│  │  │  │  │     │  │  ├─ target-04.svg
│  │  │  │  │     │  │  ├─ upload-03.svg
│  │  │  │  │     │  │  ├─ upload-cloud-01.svg
│  │  │  │  │     │  │  └─ x.svg
│  │  │  │  │     │  ├─ images
│  │  │  │  │     │  │  └─ image-plus.svg
│  │  │  │  │     │  ├─ layout
│  │  │  │  │     │  │  ├─ align-left-01.svg
│  │  │  │  │     │  │  ├─ align-right-01.svg
│  │  │  │  │     │  │  ├─ grid-01.svg
│  │  │  │  │     │  │  └─ layout-grid-02.svg
│  │  │  │  │     │  ├─ mapsAndTravel
│  │  │  │  │     │  │  ├─ globe-01.svg
│  │  │  │  │     │  │  └─ route.svg
│  │  │  │  │     │  ├─ mediaAndDevices
│  │  │  │  │     │  │  ├─ microphone-01.svg
│  │  │  │  │     │  │  ├─ play-circle.svg
│  │  │  │  │     │  │  ├─ sliders-h.svg
│  │  │  │  │     │  │  ├─ speaker.svg
│  │  │  │  │     │  │  ├─ stop-circle.svg
│  │  │  │  │     │  │  └─ stop.svg
│  │  │  │  │     │  ├─ others
│  │  │  │  │     │  │  ├─ apps-02.svg
│  │  │  │  │     │  │  ├─ colors.svg
│  │  │  │  │     │  │  ├─ drag-handle.svg
│  │  │  │  │     │  │  ├─ env.svg
│  │  │  │  │     │  │  ├─ exchange-02.svg
│  │  │  │  │     │  │  ├─ file-code.svg
│  │  │  │  │     │  │  ├─ icon-3-dots.svg
│  │  │  │  │     │  │  └─ tools.svg
│  │  │  │  │     │  ├─ shapes
│  │  │  │  │     │  │  └─ cube-outline.svg
│  │  │  │  │     │  ├─ time
│  │  │  │  │     │  │  ├─ clock-fast-forward.svg
│  │  │  │  │     │  │  ├─ clock-play-slim.svg
│  │  │  │  │     │  │  ├─ clock-play.svg
│  │  │  │  │     │  │  └─ clock-refresh.svg
│  │  │  │  │     │  ├─ users
│  │  │  │  │     │  │  ├─ user-01.svg
│  │  │  │  │     │  │  └─ users-01.svg
│  │  │  │  │     │  └─ weather
│  │  │  │  │     │     └─ stars-02.svg
│  │  │  │  │     ├─ solid
│  │  │  │  │     │  ├─ alertsAndFeedback
│  │  │  │  │     │  │  └─ alert-triangle.svg
│  │  │  │  │     │  ├─ arrows
│  │  │  │  │     │  │  ├─ chevron-down.svg
│  │  │  │  │     │  │  └─ high-priority.svg
│  │  │  │  │     │  ├─ communication
│  │  │  │  │     │  │  ├─ ai-text.svg
│  │  │  │  │     │  │  ├─ chat-bot.svg
│  │  │  │  │     │  │  ├─ cute-robote.svg
│  │  │  │  │     │  │  ├─ edit-list.svg
│  │  │  │  │     │  │  ├─ message-dots-circle.svg
│  │  │  │  │     │  │  ├─ message-fast.svg
│  │  │  │  │     │  │  ├─ message-heart-circle.svg
│  │  │  │  │     │  │  ├─ message-smile-square.svg
│  │  │  │  │     │  │  └─ send-03.svg
│  │  │  │  │     │  ├─ development
│  │  │  │  │     │  │  ├─ api-connection.svg
│  │  │  │  │     │  │  ├─ bar-chart-square-02.svg
│  │  │  │  │     │  │  ├─ container.svg
│  │  │  │  │     │  │  ├─ database-02.svg
│  │  │  │  │     │  │  ├─ database-03.svg
│  │  │  │  │     │  │  ├─ file-heart-02.svg
│  │  │  │  │     │  │  ├─ pattern-recognition.svg
│  │  │  │  │     │  │  ├─ prompt-engineering.svg
│  │  │  │  │     │  │  ├─ puzzle-piece-01.svg
│  │  │  │  │     │  │  ├─ semantic.svg
│  │  │  │  │     │  │  ├─ terminal-square.svg
│  │  │  │  │     │  │  └─ variable-02.svg
│  │  │  │  │     │  ├─ editor
│  │  │  │  │     │  │  ├─ brush-01.svg
│  │  │  │  │     │  │  ├─ citations.svg
│  │  │  │  │     │  │  ├─ colors.svg
│  │  │  │  │     │  │  ├─ paragraph.svg
│  │  │  │  │     │  │  └─ type-square.svg
│  │  │  │  │     │  ├─ education
│  │  │  │  │     │  │  ├─ beaker-02.svg
│  │  │  │  │     │  │  ├─ bubble-text.svg
│  │  │  │  │     │  │  ├─ heart-02.svg
│  │  │  │  │     │  │  └─ unblur.svg
│  │  │  │  │     │  ├─ files
│  │  │  │  │     │  │  ├─ file-05.svg
│  │  │  │  │     │  │  ├─ file-search-02.svg
│  │  │  │  │     │  │  └─ folder.svg
│  │  │  │  │     │  ├─ FinanceAndECommerce
│  │  │  │  │     │  │  ├─ gold-coin.svg
│  │  │  │  │     │  │  └─ scales-02.svg
│  │  │  │  │     │  ├─ general
│  │  │  │  │     │  │  ├─ answer-triangle.svg
│  │  │  │  │     │  │  ├─ check-circle.svg
│  │  │  │  │     │  │  ├─ check-done-01.svg
│  │  │  │  │     │  │  ├─ download-02.svg
│  │  │  │  │     │  │  ├─ edit-03.svg
│  │  │  │  │     │  │  ├─ edit-04.svg
│  │  │  │  │     │  │  ├─ eye.svg
│  │  │  │  │     │  │  ├─ message-clock-circle.svg
│  │  │  │  │     │  │  ├─ plus-circle.svg
│  │  │  │  │     │  │  ├─ question-triangle.svg
│  │  │  │  │     │  │  ├─ search-md.svg
│  │  │  │  │     │  │  ├─ target-04.svg
│  │  │  │  │     │  │  ├─ tool-03.svg
│  │  │  │  │     │  │  ├─ x-circle.svg
│  │  │  │  │     │  │  ├─ zap-fast.svg
│  │  │  │  │     │  │  └─ zap-narrow.svg
│  │  │  │  │     │  ├─ layout
│  │  │  │  │     │  │  └─ grid-01.svg
│  │  │  │  │     │  ├─ mapsAndTravel
│  │  │  │  │     │  │  ├─ globe-06.svg
│  │  │  │  │     │  │  └─ route.svg
│  │  │  │  │     │  ├─ mediaAndDevices
│  │  │  │  │     │  │  ├─ magic-box.svg
│  │  │  │  │     │  │  ├─ magic-eyes.svg
│  │  │  │  │     │  │  ├─ magic-wand.svg
│  │  │  │  │     │  │  ├─ microphone-01.svg
│  │  │  │  │     │  │  ├─ play.svg
│  │  │  │  │     │  │  ├─ robot.svg
│  │  │  │  │     │  │  ├─ sliders-02.svg
│  │  │  │  │     │  │  ├─ speaker.svg
│  │  │  │  │     │  │  └─ stop-circle.svg
│  │  │  │  │     │  ├─ security
│  │  │  │  │     │  │  └─ lock-01.svg
│  │  │  │  │     │  ├─ shapes
│  │  │  │  │     │  │  ├─ star-04.svg
│  │  │  │  │     │  │  └─ star-06.svg
│  │  │  │  │     │  └─ users
│  │  │  │  │     │     ├─ user-01.svg
│  │  │  │  │     │     ├─ user-edit-02.svg
│  │  │  │  │     │     └─ users-01.svg
│  │  │  │  │     └─ workflow
│  │  │  │  │        ├─ answer.svg
│  │  │  │  │        ├─ code.svg
│  │  │  │  │        ├─ end.svg
│  │  │  │  │        ├─ home.svg
│  │  │  │  │        ├─ http.svg
│  │  │  │  │        ├─ if-else.svg
│  │  │  │  │        ├─ iteration-start.svg
│  │  │  │  │        ├─ iteration.svg
│  │  │  │  │        ├─ jinja.svg
│  │  │  │  │        ├─ knowledge-retrieval.svg
│  │  │  │  │        ├─ llm.svg
│  │  │  │  │        ├─ parameter-extractor.svg
│  │  │  │  │        ├─ question-classifier.svg
│  │  │  │  │        ├─ templating-transform.svg
│  │  │  │  │        └─ variable-x.svg
│  │  │  │  ├─ IconBase.tsx
│  │  │  │  ├─ script.js
│  │  │  │  ├─ src
│  │  │  │  │  ├─ image
│  │  │  │  │  │  └─ llm
│  │  │  │  │  │     ├─ BaichuanTextCn.module.css
│  │  │  │  │  │     ├─ BaichuanTextCn.tsx
│  │  │  │  │  │     ├─ index.ts
│  │  │  │  │  │     ├─ Minimax.module.css
│  │  │  │  │  │     ├─ Minimax.tsx
│  │  │  │  │  │     ├─ MinimaxText.module.css
│  │  │  │  │  │     ├─ MinimaxText.tsx
│  │  │  │  │  │     ├─ Tongyi.module.css
│  │  │  │  │  │     ├─ Tongyi.tsx
│  │  │  │  │  │     ├─ TongyiText.module.css
│  │  │  │  │  │     ├─ TongyiText.tsx
│  │  │  │  │  │     ├─ TongyiTextCn.module.css
│  │  │  │  │  │     ├─ TongyiTextCn.tsx
│  │  │  │  │  │     ├─ Wxyy.module.css
│  │  │  │  │  │     ├─ Wxyy.tsx
│  │  │  │  │  │     ├─ WxyyText.module.css
│  │  │  │  │  │     ├─ WxyyText.tsx
│  │  │  │  │  │     ├─ WxyyTextCn.module.css
│  │  │  │  │  │     └─ WxyyTextCn.tsx
│  │  │  │  │  ├─ public
│  │  │  │  │  │  ├─ avatar
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Robot.json
│  │  │  │  │  │  │  ├─ Robot.tsx
│  │  │  │  │  │  │  ├─ User.json
│  │  │  │  │  │  │  └─ User.tsx
│  │  │  │  │  │  ├─ billing
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Sparkles.json
│  │  │  │  │  │  │  └─ Sparkles.tsx
│  │  │  │  │  │  ├─ common
│  │  │  │  │  │  │  ├─ D.json
│  │  │  │  │  │  │  ├─ D.tsx
│  │  │  │  │  │  │  ├─ DiagonalDividingLine.json
│  │  │  │  │  │  │  ├─ DiagonalDividingLine.tsx
│  │  │  │  │  │  │  ├─ Dify.json
│  │  │  │  │  │  │  ├─ Dify.tsx
│  │  │  │  │  │  │  ├─ Github.json
│  │  │  │  │  │  │  ├─ Github.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Line3.json
│  │  │  │  │  │  │  ├─ Line3.tsx
│  │  │  │  │  │  │  ├─ MessageChatSquare.json
│  │  │  │  │  │  │  ├─ MessageChatSquare.tsx
│  │  │  │  │  │  │  ├─ MultiPathRetrieval.json
│  │  │  │  │  │  │  ├─ MultiPathRetrieval.tsx
│  │  │  │  │  │  │  ├─ Notion.json
│  │  │  │  │  │  │  ├─ Notion.tsx
│  │  │  │  │  │  │  ├─ NTo1Retrieval.json
│  │  │  │  │  │  │  └─ NTo1Retrieval.tsx
│  │  │  │  │  │  ├─ files
│  │  │  │  │  │  │  ├─ Csv.json
│  │  │  │  │  │  │  ├─ Csv.tsx
│  │  │  │  │  │  │  ├─ Doc.json
│  │  │  │  │  │  │  ├─ Doc.tsx
│  │  │  │  │  │  │  ├─ Docx.json
│  │  │  │  │  │  │  ├─ Docx.tsx
│  │  │  │  │  │  │  ├─ Html.json
│  │  │  │  │  │  │  ├─ Html.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Json.json
│  │  │  │  │  │  │  ├─ Json.tsx
│  │  │  │  │  │  │  ├─ Md.json
│  │  │  │  │  │  │  ├─ Md.tsx
│  │  │  │  │  │  │  ├─ Pdf.json
│  │  │  │  │  │  │  ├─ Pdf.tsx
│  │  │  │  │  │  │  ├─ Txt.json
│  │  │  │  │  │  │  ├─ Txt.tsx
│  │  │  │  │  │  │  ├─ Unknow.json
│  │  │  │  │  │  │  ├─ Unknow.tsx
│  │  │  │  │  │  │  ├─ Xlsx.json
│  │  │  │  │  │  │  ├─ Xlsx.tsx
│  │  │  │  │  │  │  ├─ Yaml.json
│  │  │  │  │  │  │  └─ Yaml.tsx
│  │  │  │  │  │  ├─ llm
│  │  │  │  │  │  │  ├─ Anthropic.json
│  │  │  │  │  │  │  ├─ Anthropic.tsx
│  │  │  │  │  │  │  ├─ AnthropicText.json
│  │  │  │  │  │  │  ├─ AnthropicText.tsx
│  │  │  │  │  │  │  ├─ Azureai.json
│  │  │  │  │  │  │  ├─ Azureai.tsx
│  │  │  │  │  │  │  ├─ AzureaiText.json
│  │  │  │  │  │  │  ├─ AzureaiText.tsx
│  │  │  │  │  │  │  ├─ AzureOpenaiService.json
│  │  │  │  │  │  │  ├─ AzureOpenaiService.tsx
│  │  │  │  │  │  │  ├─ AzureOpenaiServiceText.json
│  │  │  │  │  │  │  ├─ AzureOpenaiServiceText.tsx
│  │  │  │  │  │  │  ├─ Baichuan.json
│  │  │  │  │  │  │  ├─ Baichuan.tsx
│  │  │  │  │  │  │  ├─ BaichuanText.json
│  │  │  │  │  │  │  ├─ BaichuanText.tsx
│  │  │  │  │  │  │  ├─ Chatglm.json
│  │  │  │  │  │  │  ├─ Chatglm.tsx
│  │  │  │  │  │  │  ├─ ChatglmText.json
│  │  │  │  │  │  │  ├─ ChatglmText.tsx
│  │  │  │  │  │  │  ├─ Cohere.json
│  │  │  │  │  │  │  ├─ Cohere.tsx
│  │  │  │  │  │  │  ├─ CohereText.json
│  │  │  │  │  │  │  ├─ CohereText.tsx
│  │  │  │  │  │  │  ├─ Gpt3.json
│  │  │  │  │  │  │  ├─ Gpt3.tsx
│  │  │  │  │  │  │  ├─ Gpt4.json
│  │  │  │  │  │  │  ├─ Gpt4.tsx
│  │  │  │  │  │  │  ├─ Huggingface.json
│  │  │  │  │  │  │  ├─ Huggingface.tsx
│  │  │  │  │  │  │  ├─ HuggingfaceText.json
│  │  │  │  │  │  │  ├─ HuggingfaceText.tsx
│  │  │  │  │  │  │  ├─ HuggingfaceTextHub.json
│  │  │  │  │  │  │  ├─ HuggingfaceTextHub.tsx
│  │  │  │  │  │  │  ├─ IflytekSpark.json
│  │  │  │  │  │  │  ├─ IflytekSpark.tsx
│  │  │  │  │  │  │  ├─ IflytekSparkText.json
│  │  │  │  │  │  │  ├─ IflytekSparkText.tsx
│  │  │  │  │  │  │  ├─ IflytekSparkTextCn.json
│  │  │  │  │  │  │  ├─ IflytekSparkTextCn.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Jina.json
│  │  │  │  │  │  │  ├─ Jina.tsx
│  │  │  │  │  │  │  ├─ JinaText.json
│  │  │  │  │  │  │  ├─ JinaText.tsx
│  │  │  │  │  │  │  ├─ Localai.json
│  │  │  │  │  │  │  ├─ Localai.tsx
│  │  │  │  │  │  │  ├─ LocalaiText.json
│  │  │  │  │  │  │  ├─ LocalaiText.tsx
│  │  │  │  │  │  │  ├─ Microsoft.json
│  │  │  │  │  │  │  ├─ Microsoft.tsx
│  │  │  │  │  │  │  ├─ OpenaiBlack.json
│  │  │  │  │  │  │  ├─ OpenaiBlack.tsx
│  │  │  │  │  │  │  ├─ OpenaiBlue.json
│  │  │  │  │  │  │  ├─ OpenaiBlue.tsx
│  │  │  │  │  │  │  ├─ OpenaiGreen.json
│  │  │  │  │  │  │  ├─ OpenaiGreen.tsx
│  │  │  │  │  │  │  ├─ OpenaiText.json
│  │  │  │  │  │  │  ├─ OpenaiText.tsx
│  │  │  │  │  │  │  ├─ OpenaiTransparent.json
│  │  │  │  │  │  │  ├─ OpenaiTransparent.tsx
│  │  │  │  │  │  │  ├─ OpenaiViolet.json
│  │  │  │  │  │  │  ├─ OpenaiViolet.tsx
│  │  │  │  │  │  │  ├─ Openllm.json
│  │  │  │  │  │  │  ├─ Openllm.tsx
│  │  │  │  │  │  │  ├─ OpenllmText.json
│  │  │  │  │  │  │  ├─ OpenllmText.tsx
│  │  │  │  │  │  │  ├─ Replicate.json
│  │  │  │  │  │  │  ├─ Replicate.tsx
│  │  │  │  │  │  │  ├─ ReplicateText.json
│  │  │  │  │  │  │  ├─ ReplicateText.tsx
│  │  │  │  │  │  │  ├─ XorbitsInference.json
│  │  │  │  │  │  │  ├─ XorbitsInference.tsx
│  │  │  │  │  │  │  ├─ XorbitsInferenceText.json
│  │  │  │  │  │  │  ├─ XorbitsInferenceText.tsx
│  │  │  │  │  │  │  ├─ Zhipuai.json
│  │  │  │  │  │  │  ├─ Zhipuai.tsx
│  │  │  │  │  │  │  ├─ ZhipuaiText.json
│  │  │  │  │  │  │  ├─ ZhipuaiText.tsx
│  │  │  │  │  │  │  ├─ ZhipuaiTextCn.json
│  │  │  │  │  │  │  └─ ZhipuaiTextCn.tsx
│  │  │  │  │  │  ├─ model
│  │  │  │  │  │  │  ├─ Checked.json
│  │  │  │  │  │  │  ├─ Checked.tsx
│  │  │  │  │  │  │  └─ index.ts
│  │  │  │  │  │  ├─ other
│  │  │  │  │  │  │  ├─ DefaultToolIcon.json
│  │  │  │  │  │  │  ├─ DefaultToolIcon.tsx
│  │  │  │  │  │  │  ├─ Icon3Dots.json
│  │  │  │  │  │  │  ├─ Icon3Dots.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ RowStruct.json
│  │  │  │  │  │  │  └─ RowStruct.tsx
│  │  │  │  │  │  ├─ plugins
│  │  │  │  │  │  │  ├─ Google.json
│  │  │  │  │  │  │  ├─ Google.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ WebReader.json
│  │  │  │  │  │  │  ├─ WebReader.tsx
│  │  │  │  │  │  │  ├─ Wikipedia.json
│  │  │  │  │  │  │  └─ Wikipedia.tsx
│  │  │  │  │  │  ├─ thought
│  │  │  │  │  │  │  ├─ DataSet.json
│  │  │  │  │  │  │  ├─ DataSet.tsx
│  │  │  │  │  │  │  ├─ index.ts
│  │  │  │  │  │  │  ├─ Loading.json
│  │  │  │  │  │  │  ├─ Loading.tsx
│  │  │  │  │  │  │  ├─ Search.json
│  │  │  │  │  │  │  ├─ Search.tsx
│  │  │  │  │  │  │  ├─ ThoughtList.json
│  │  │  │  │  │  │  ├─ ThoughtList.tsx
│  │  │  │  │  │  │  ├─ WebReader.json
│  │  │  │  │  │  │  └─ WebReader.tsx
│  │  │  │  │  │  └─ tracing
│  │  │  │  │  │     ├─ index.ts
│  │  │  │  │  │     ├─ LangfuseIcon.json
│  │  │  │  │  │     ├─ LangfuseIcon.tsx
│  │  │  │  │  │     ├─ LangfuseIconBig.json
│  │  │  │  │  │     ├─ LangfuseIconBig.tsx
│  │  │  │  │  │     ├─ LangsmithIcon.json
│  │  │  │  │  │     ├─ LangsmithIcon.tsx
│  │  │  │  │  │     ├─ LangsmithIconBig.json
│  │  │  │  │  │     ├─ LangsmithIconBig.tsx
│  │  │  │  │  │     ├─ TracingIcon.json
│  │  │  │  │  │     └─ TracingIcon.tsx
│  │  │  │  │  └─ vender
│  │  │  │  │     ├─ line
│  │  │  │  │     │  ├─ alertsAndFeedback
│  │  │  │  │     │  │  ├─ AlertTriangle.json
│  │  │  │  │     │  │  ├─ AlertTriangle.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ ThumbsDown.json
│  │  │  │  │     │  │  ├─ ThumbsDown.tsx
│  │  │  │  │     │  │  ├─ ThumbsUp.json
│  │  │  │  │     │  │  └─ ThumbsUp.tsx
│  │  │  │  │     │  ├─ arrows
│  │  │  │  │     │  │  ├─ ArrowNarrowLeft.json
│  │  │  │  │     │  │  ├─ ArrowNarrowLeft.tsx
│  │  │  │  │     │  │  ├─ ArrowUpRight.json
│  │  │  │  │     │  │  ├─ ArrowUpRight.tsx
│  │  │  │  │     │  │  ├─ ChevronDownDouble.json
│  │  │  │  │     │  │  ├─ ChevronDownDouble.tsx
│  │  │  │  │     │  │  ├─ ChevronRight.json
│  │  │  │  │     │  │  ├─ ChevronRight.tsx
│  │  │  │  │     │  │  ├─ ChevronSelectorVertical.json
│  │  │  │  │     │  │  ├─ ChevronSelectorVertical.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ RefreshCcw01.json
│  │  │  │  │     │  │  ├─ RefreshCcw01.tsx
│  │  │  │  │     │  │  ├─ RefreshCw05.json
│  │  │  │  │     │  │  ├─ RefreshCw05.tsx
│  │  │  │  │     │  │  ├─ ReverseLeft.json
│  │  │  │  │     │  │  └─ ReverseLeft.tsx
│  │  │  │  │     │  ├─ communication
│  │  │  │  │     │  │  ├─ AiText.json
│  │  │  │  │     │  │  ├─ AiText.tsx
│  │  │  │  │     │  │  ├─ ChatBot.json
│  │  │  │  │     │  │  ├─ ChatBot.tsx
│  │  │  │  │     │  │  ├─ ChatBotSlim.json
│  │  │  │  │     │  │  ├─ ChatBotSlim.tsx
│  │  │  │  │     │  │  ├─ CuteRobot.json
│  │  │  │  │     │  │  ├─ CuteRobot.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ MessageCheckRemove.json
│  │  │  │  │     │  │  ├─ MessageCheckRemove.tsx
│  │  │  │  │     │  │  ├─ MessageFastPlus.json
│  │  │  │  │     │  │  └─ MessageFastPlus.tsx
│  │  │  │  │     │  ├─ development
│  │  │  │  │     │  │  ├─ ArtificialBrain.json
│  │  │  │  │     │  │  ├─ ArtificialBrain.tsx
│  │  │  │  │     │  │  ├─ BarChartSquare02.json
│  │  │  │  │     │  │  ├─ BarChartSquare02.tsx
│  │  │  │  │     │  │  ├─ BracketsX.json
│  │  │  │  │     │  │  ├─ BracketsX.tsx
│  │  │  │  │     │  │  ├─ CodeBrowser.json
│  │  │  │  │     │  │  ├─ CodeBrowser.tsx
│  │  │  │  │     │  │  ├─ Container.json
│  │  │  │  │     │  │  ├─ Container.tsx
│  │  │  │  │     │  │  ├─ Database01.json
│  │  │  │  │     │  │  ├─ Database01.tsx
│  │  │  │  │     │  │  ├─ Database03.json
│  │  │  │  │     │  │  ├─ Database03.tsx
│  │  │  │  │     │  │  ├─ FileHeart02.json
│  │  │  │  │     │  │  ├─ FileHeart02.tsx
│  │  │  │  │     │  │  ├─ GitBranch01.json
│  │  │  │  │     │  │  ├─ GitBranch01.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ PromptEngineering.json
│  │  │  │  │     │  │  ├─ PromptEngineering.tsx
│  │  │  │  │     │  │  ├─ PuzzlePiece01.json
│  │  │  │  │     │  │  ├─ PuzzlePiece01.tsx
│  │  │  │  │     │  │  ├─ TerminalSquare.json
│  │  │  │  │     │  │  ├─ TerminalSquare.tsx
│  │  │  │  │     │  │  ├─ Variable.json
│  │  │  │  │     │  │  ├─ Variable.tsx
│  │  │  │  │     │  │  ├─ Webhooks.json
│  │  │  │  │     │  │  └─ Webhooks.tsx
│  │  │  │  │     │  ├─ editor
│  │  │  │  │     │  │  ├─ AlignLeft.json
│  │  │  │  │     │  │  ├─ AlignLeft.tsx
│  │  │  │  │     │  │  ├─ BezierCurve03.json
│  │  │  │  │     │  │  ├─ BezierCurve03.tsx
│  │  │  │  │     │  │  ├─ Colors.json
│  │  │  │  │     │  │  ├─ Colors.tsx
│  │  │  │  │     │  │  ├─ ImageIndentLeft.json
│  │  │  │  │     │  │  ├─ ImageIndentLeft.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ LeftIndent02.json
│  │  │  │  │     │  │  ├─ LeftIndent02.tsx
│  │  │  │  │     │  │  ├─ LetterSpacing01.json
│  │  │  │  │     │  │  ├─ LetterSpacing01.tsx
│  │  │  │  │     │  │  ├─ TypeSquare.json
│  │  │  │  │     │  │  └─ TypeSquare.tsx
│  │  │  │  │     │  ├─ education
│  │  │  │  │     │  │  ├─ BookOpen01.json
│  │  │  │  │     │  │  ├─ BookOpen01.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ files
│  │  │  │  │     │  │  ├─ Clipboard.json
│  │  │  │  │     │  │  ├─ Clipboard.tsx
│  │  │  │  │     │  │  ├─ ClipboardCheck.json
│  │  │  │  │     │  │  ├─ ClipboardCheck.tsx
│  │  │  │  │     │  │  ├─ File02.json
│  │  │  │  │     │  │  ├─ File02.tsx
│  │  │  │  │     │  │  ├─ FileArrow01.json
│  │  │  │  │     │  │  ├─ FileArrow01.tsx
│  │  │  │  │     │  │  ├─ FileCheck02.json
│  │  │  │  │     │  │  ├─ FileCheck02.tsx
│  │  │  │  │     │  │  ├─ FileDownload02.json
│  │  │  │  │     │  │  ├─ FileDownload02.tsx
│  │  │  │  │     │  │  ├─ FilePlus01.json
│  │  │  │  │     │  │  ├─ FilePlus01.tsx
│  │  │  │  │     │  │  ├─ FilePlus02.json
│  │  │  │  │     │  │  ├─ FilePlus02.tsx
│  │  │  │  │     │  │  ├─ FileText.json
│  │  │  │  │     │  │  ├─ FileText.tsx
│  │  │  │  │     │  │  ├─ FileUpload.json
│  │  │  │  │     │  │  ├─ FileUpload.tsx
│  │  │  │  │     │  │  ├─ Folder.json
│  │  │  │  │     │  │  ├─ Folder.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ financeAndECommerce
│  │  │  │  │     │  │  ├─ Balance.json
│  │  │  │  │     │  │  ├─ Balance.tsx
│  │  │  │  │     │  │  ├─ CoinsStacked01.json
│  │  │  │  │     │  │  ├─ CoinsStacked01.tsx
│  │  │  │  │     │  │  ├─ GoldCoin.json
│  │  │  │  │     │  │  ├─ GoldCoin.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ ReceiptList.json
│  │  │  │  │     │  │  ├─ ReceiptList.tsx
│  │  │  │  │     │  │  ├─ Tag01.json
│  │  │  │  │     │  │  ├─ Tag01.tsx
│  │  │  │  │     │  │  ├─ Tag03.json
│  │  │  │  │     │  │  └─ Tag03.tsx
│  │  │  │  │     │  ├─ general
│  │  │  │  │     │  │  ├─ AtSign.json
│  │  │  │  │     │  │  ├─ AtSign.tsx
│  │  │  │  │     │  │  ├─ Bookmark.json
│  │  │  │  │     │  │  ├─ Bookmark.tsx
│  │  │  │  │     │  │  ├─ Check.json
│  │  │  │  │     │  │  ├─ Check.tsx
│  │  │  │  │     │  │  ├─ CheckDone01.json
│  │  │  │  │     │  │  ├─ CheckDone01.tsx
│  │  │  │  │     │  │  ├─ ChecklistSquare.json
│  │  │  │  │     │  │  ├─ ChecklistSquare.tsx
│  │  │  │  │     │  │  ├─ DotsGrid.json
│  │  │  │  │     │  │  ├─ DotsGrid.tsx
│  │  │  │  │     │  │  ├─ Edit02.json
│  │  │  │  │     │  │  ├─ Edit02.tsx
│  │  │  │  │     │  │  ├─ Edit04.json
│  │  │  │  │     │  │  ├─ Edit04.tsx
│  │  │  │  │     │  │  ├─ Edit05.json
│  │  │  │  │     │  │  ├─ Edit05.tsx
│  │  │  │  │     │  │  ├─ Hash02.json
│  │  │  │  │     │  │  ├─ Hash02.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ InfoCircle.json
│  │  │  │  │     │  │  ├─ InfoCircle.tsx
│  │  │  │  │     │  │  ├─ Link03.json
│  │  │  │  │     │  │  ├─ Link03.tsx
│  │  │  │  │     │  │  ├─ LinkExternal02.json
│  │  │  │  │     │  │  ├─ LinkExternal02.tsx
│  │  │  │  │     │  │  ├─ LogIn04.json
│  │  │  │  │     │  │  ├─ LogIn04.tsx
│  │  │  │  │     │  │  ├─ LogOut01.json
│  │  │  │  │     │  │  ├─ LogOut01.tsx
│  │  │  │  │     │  │  ├─ LogOut04.json
│  │  │  │  │     │  │  ├─ LogOut04.tsx
│  │  │  │  │     │  │  ├─ Menu01.json
│  │  │  │  │     │  │  ├─ Menu01.tsx
│  │  │  │  │     │  │  ├─ Pin01.json
│  │  │  │  │     │  │  ├─ Pin01.tsx
│  │  │  │  │     │  │  ├─ Pin02.json
│  │  │  │  │     │  │  ├─ Pin02.tsx
│  │  │  │  │     │  │  ├─ Plus02.json
│  │  │  │  │     │  │  ├─ Plus02.tsx
│  │  │  │  │     │  │  ├─ Settings01.json
│  │  │  │  │     │  │  ├─ Settings01.tsx
│  │  │  │  │     │  │  ├─ Settings04.json
│  │  │  │  │     │  │  ├─ Settings04.tsx
│  │  │  │  │     │  │  ├─ Target04.json
│  │  │  │  │     │  │  ├─ Target04.tsx
│  │  │  │  │     │  │  ├─ Upload03.json
│  │  │  │  │     │  │  ├─ Upload03.tsx
│  │  │  │  │     │  │  ├─ UploadCloud01.json
│  │  │  │  │     │  │  ├─ UploadCloud01.tsx
│  │  │  │  │     │  │  ├─ X.json
│  │  │  │  │     │  │  └─ X.tsx
│  │  │  │  │     │  ├─ images
│  │  │  │  │     │  │  ├─ ImagePlus.json
│  │  │  │  │     │  │  ├─ ImagePlus.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ layout
│  │  │  │  │     │  │  ├─ AlignLeft01.json
│  │  │  │  │     │  │  ├─ AlignLeft01.tsx
│  │  │  │  │     │  │  ├─ AlignRight01.json
│  │  │  │  │     │  │  ├─ AlignRight01.tsx
│  │  │  │  │     │  │  ├─ Grid01.json
│  │  │  │  │     │  │  ├─ Grid01.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ LayoutGrid02.json
│  │  │  │  │     │  │  └─ LayoutGrid02.tsx
│  │  │  │  │     │  ├─ mapsAndTravel
│  │  │  │  │     │  │  ├─ Globe01.json
│  │  │  │  │     │  │  ├─ Globe01.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Route.json
│  │  │  │  │     │  │  └─ Route.tsx
│  │  │  │  │     │  ├─ mediaAndDevices
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Microphone01.json
│  │  │  │  │     │  │  ├─ Microphone01.tsx
│  │  │  │  │     │  │  ├─ PlayCircle.json
│  │  │  │  │     │  │  ├─ PlayCircle.tsx
│  │  │  │  │     │  │  ├─ SlidersH.json
│  │  │  │  │     │  │  ├─ SlidersH.tsx
│  │  │  │  │     │  │  ├─ Speaker.json
│  │  │  │  │     │  │  ├─ Speaker.tsx
│  │  │  │  │     │  │  ├─ Stop.json
│  │  │  │  │     │  │  ├─ Stop.tsx
│  │  │  │  │     │  │  ├─ StopCircle.json
│  │  │  │  │     │  │  └─ StopCircle.tsx
│  │  │  │  │     │  ├─ others
│  │  │  │  │     │  │  ├─ Apps02.json
│  │  │  │  │     │  │  ├─ Apps02.tsx
│  │  │  │  │     │  │  ├─ Colors.json
│  │  │  │  │     │  │  ├─ Colors.tsx
│  │  │  │  │     │  │  ├─ DragHandle.json
│  │  │  │  │     │  │  ├─ DragHandle.tsx
│  │  │  │  │     │  │  ├─ Env.json
│  │  │  │  │     │  │  ├─ Env.tsx
│  │  │  │  │     │  │  ├─ Exchange02.json
│  │  │  │  │     │  │  ├─ Exchange02.tsx
│  │  │  │  │     │  │  ├─ FileCode.json
│  │  │  │  │     │  │  ├─ FileCode.tsx
│  │  │  │  │     │  │  ├─ Icon3Dots.json
│  │  │  │  │     │  │  ├─ Icon3Dots.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Tools.json
│  │  │  │  │     │  │  └─ Tools.tsx
│  │  │  │  │     │  ├─ shapes
│  │  │  │  │     │  │  ├─ CubeOutline.json
│  │  │  │  │     │  │  ├─ CubeOutline.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ time
│  │  │  │  │     │  │  ├─ ClockFastForward.json
│  │  │  │  │     │  │  ├─ ClockFastForward.tsx
│  │  │  │  │     │  │  ├─ ClockPlay.json
│  │  │  │  │     │  │  ├─ ClockPlay.tsx
│  │  │  │  │     │  │  ├─ ClockPlaySlim.json
│  │  │  │  │     │  │  ├─ ClockPlaySlim.tsx
│  │  │  │  │     │  │  ├─ ClockRefresh.json
│  │  │  │  │     │  │  ├─ ClockRefresh.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ users
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ User01.json
│  │  │  │  │     │  │  ├─ User01.tsx
│  │  │  │  │     │  │  ├─ Users01.json
│  │  │  │  │     │  │  └─ Users01.tsx
│  │  │  │  │     │  └─ weather
│  │  │  │  │     │     ├─ index.ts
│  │  │  │  │     │     ├─ Stars02.json
│  │  │  │  │     │     └─ Stars02.tsx
│  │  │  │  │     ├─ solid
│  │  │  │  │     │  ├─ alertsAndFeedback
│  │  │  │  │     │  │  ├─ AlertTriangle.json
│  │  │  │  │     │  │  ├─ AlertTriangle.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ arrows
│  │  │  │  │     │  │  ├─ ChevronDown.json
│  │  │  │  │     │  │  ├─ ChevronDown.tsx
│  │  │  │  │     │  │  ├─ HighPriority.json
│  │  │  │  │     │  │  ├─ HighPriority.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ communication
│  │  │  │  │     │  │  ├─ AiText.json
│  │  │  │  │     │  │  ├─ AiText.tsx
│  │  │  │  │     │  │  ├─ ChatBot.json
│  │  │  │  │     │  │  ├─ ChatBot.tsx
│  │  │  │  │     │  │  ├─ CuteRobote.json
│  │  │  │  │     │  │  ├─ CuteRobote.tsx
│  │  │  │  │     │  │  ├─ EditList.json
│  │  │  │  │     │  │  ├─ EditList.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ MessageDotsCircle.json
│  │  │  │  │     │  │  ├─ MessageDotsCircle.tsx
│  │  │  │  │     │  │  ├─ MessageFast.json
│  │  │  │  │     │  │  ├─ MessageFast.tsx
│  │  │  │  │     │  │  ├─ MessageHeartCircle.json
│  │  │  │  │     │  │  ├─ MessageHeartCircle.tsx
│  │  │  │  │     │  │  ├─ MessageSmileSquare.json
│  │  │  │  │     │  │  ├─ MessageSmileSquare.tsx
│  │  │  │  │     │  │  ├─ Send03.json
│  │  │  │  │     │  │  └─ Send03.tsx
│  │  │  │  │     │  ├─ development
│  │  │  │  │     │  │  ├─ ApiConnection.json
│  │  │  │  │     │  │  ├─ ApiConnection.tsx
│  │  │  │  │     │  │  ├─ BarChartSquare02.json
│  │  │  │  │     │  │  ├─ BarChartSquare02.tsx
│  │  │  │  │     │  │  ├─ Container.json
│  │  │  │  │     │  │  ├─ Container.tsx
│  │  │  │  │     │  │  ├─ Database02.json
│  │  │  │  │     │  │  ├─ Database02.tsx
│  │  │  │  │     │  │  ├─ Database03.json
│  │  │  │  │     │  │  ├─ Database03.tsx
│  │  │  │  │     │  │  ├─ FileHeart02.json
│  │  │  │  │     │  │  ├─ FileHeart02.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ PatternRecognition.json
│  │  │  │  │     │  │  ├─ PatternRecognition.tsx
│  │  │  │  │     │  │  ├─ PromptEngineering.json
│  │  │  │  │     │  │  ├─ PromptEngineering.tsx
│  │  │  │  │     │  │  ├─ PuzzlePiece01.json
│  │  │  │  │     │  │  ├─ PuzzlePiece01.tsx
│  │  │  │  │     │  │  ├─ Semantic.json
│  │  │  │  │     │  │  ├─ Semantic.tsx
│  │  │  │  │     │  │  ├─ TerminalSquare.json
│  │  │  │  │     │  │  ├─ TerminalSquare.tsx
│  │  │  │  │     │  │  ├─ Variable02.json
│  │  │  │  │     │  │  └─ Variable02.tsx
│  │  │  │  │     │  ├─ editor
│  │  │  │  │     │  │  ├─ Brush01.json
│  │  │  │  │     │  │  ├─ Brush01.tsx
│  │  │  │  │     │  │  ├─ Citations.json
│  │  │  │  │     │  │  ├─ Citations.tsx
│  │  │  │  │     │  │  ├─ Colors.json
│  │  │  │  │     │  │  ├─ Colors.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Paragraph.json
│  │  │  │  │     │  │  ├─ Paragraph.tsx
│  │  │  │  │     │  │  ├─ TypeSquare.json
│  │  │  │  │     │  │  └─ TypeSquare.tsx
│  │  │  │  │     │  ├─ education
│  │  │  │  │     │  │  ├─ Beaker02.json
│  │  │  │  │     │  │  ├─ Beaker02.tsx
│  │  │  │  │     │  │  ├─ BubbleText.json
│  │  │  │  │     │  │  ├─ BubbleText.tsx
│  │  │  │  │     │  │  ├─ Heart02.json
│  │  │  │  │     │  │  ├─ Heart02.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Unblur.json
│  │  │  │  │     │  │  └─ Unblur.tsx
│  │  │  │  │     │  ├─ files
│  │  │  │  │     │  │  ├─ File05.json
│  │  │  │  │     │  │  ├─ File05.tsx
│  │  │  │  │     │  │  ├─ FileSearch02.json
│  │  │  │  │     │  │  ├─ FileSearch02.tsx
│  │  │  │  │     │  │  ├─ Folder.json
│  │  │  │  │     │  │  ├─ Folder.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ FinanceAndECommerce
│  │  │  │  │     │  │  ├─ GoldCoin.json
│  │  │  │  │     │  │  ├─ GoldCoin.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Scales02.json
│  │  │  │  │     │  │  └─ Scales02.tsx
│  │  │  │  │     │  ├─ general
│  │  │  │  │     │  │  ├─ AnswerTriangle.json
│  │  │  │  │     │  │  ├─ AnswerTriangle.tsx
│  │  │  │  │     │  │  ├─ CheckCircle.json
│  │  │  │  │     │  │  ├─ CheckCircle.tsx
│  │  │  │  │     │  │  ├─ CheckDone01.json
│  │  │  │  │     │  │  ├─ CheckDone01.tsx
│  │  │  │  │     │  │  ├─ Download02.json
│  │  │  │  │     │  │  ├─ Download02.tsx
│  │  │  │  │     │  │  ├─ Edit03.json
│  │  │  │  │     │  │  ├─ Edit03.tsx
│  │  │  │  │     │  │  ├─ Edit04.json
│  │  │  │  │     │  │  ├─ Edit04.tsx
│  │  │  │  │     │  │  ├─ Eye.json
│  │  │  │  │     │  │  ├─ Eye.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ MessageClockCircle.json
│  │  │  │  │     │  │  ├─ MessageClockCircle.tsx
│  │  │  │  │     │  │  ├─ PlusCircle.json
│  │  │  │  │     │  │  ├─ PlusCircle.tsx
│  │  │  │  │     │  │  ├─ QuestionTriangle.json
│  │  │  │  │     │  │  ├─ QuestionTriangle.tsx
│  │  │  │  │     │  │  ├─ SearchMd.json
│  │  │  │  │     │  │  ├─ SearchMd.tsx
│  │  │  │  │     │  │  ├─ Target04.json
│  │  │  │  │     │  │  ├─ Target04.tsx
│  │  │  │  │     │  │  ├─ Tool03.json
│  │  │  │  │     │  │  ├─ Tool03.tsx
│  │  │  │  │     │  │  ├─ XCircle.json
│  │  │  │  │     │  │  ├─ XCircle.tsx
│  │  │  │  │     │  │  ├─ ZapFast.json
│  │  │  │  │     │  │  ├─ ZapFast.tsx
│  │  │  │  │     │  │  ├─ ZapNarrow.json
│  │  │  │  │     │  │  └─ ZapNarrow.tsx
│  │  │  │  │     │  ├─ layout
│  │  │  │  │     │  │  ├─ Grid01.json
│  │  │  │  │     │  │  ├─ Grid01.tsx
│  │  │  │  │     │  │  └─ index.ts
│  │  │  │  │     │  ├─ mapsAndTravel
│  │  │  │  │     │  │  ├─ Globe06.json
│  │  │  │  │     │  │  ├─ Globe06.tsx
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Route.json
│  │  │  │  │     │  │  └─ Route.tsx
│  │  │  │  │     │  ├─ mediaAndDevices
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ MagicBox.json
│  │  │  │  │     │  │  ├─ MagicBox.tsx
│  │  │  │  │     │  │  ├─ MagicEyes.json
│  │  │  │  │     │  │  ├─ MagicEyes.tsx
│  │  │  │  │     │  │  ├─ MagicWand.json
│  │  │  │  │     │  │  ├─ MagicWand.tsx
│  │  │  │  │     │  │  ├─ Microphone01.json
│  │  │  │  │     │  │  ├─ Microphone01.tsx
│  │  │  │  │     │  │  ├─ Play.json
│  │  │  │  │     │  │  ├─ Play.tsx
│  │  │  │  │     │  │  ├─ Robot.json
│  │  │  │  │     │  │  ├─ Robot.tsx
│  │  │  │  │     │  │  ├─ Sliders02.json
│  │  │  │  │     │  │  ├─ Sliders02.tsx
│  │  │  │  │     │  │  ├─ Speaker.json
│  │  │  │  │     │  │  ├─ Speaker.tsx
│  │  │  │  │     │  │  ├─ StopCircle.json
│  │  │  │  │     │  │  └─ StopCircle.tsx
│  │  │  │  │     │  ├─ security
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Lock01.json
│  │  │  │  │     │  │  └─ Lock01.tsx
│  │  │  │  │     │  ├─ shapes
│  │  │  │  │     │  │  ├─ index.ts
│  │  │  │  │     │  │  ├─ Star04.json
│  │  │  │  │     │  │  ├─ Star04.tsx
│  │  │  │  │     │  │  ├─ Star06.json
│  │  │  │  │     │  │  └─ Star06.tsx
│  │  │  │  │     │  └─ users
│  │  │  │  │     │     ├─ index.ts
│  │  │  │  │     │     ├─ User01.json
│  │  │  │  │     │     ├─ User01.tsx
│  │  │  │  │     │     ├─ UserEdit02.json
│  │  │  │  │     │     ├─ UserEdit02.tsx
│  │  │  │  │     │     ├─ Users01.json
│  │  │  │  │     │     └─ Users01.tsx
│  │  │  │  │     └─ workflow
│  │  │  │  │        ├─ AgentNode.json
│  │  │  │  │        ├─ AgentNode.tsx
│  │  │  │  │        ├─ Answer.json
│  │  │  │  │        ├─ Answer.tsx
│  │  │  │  │        ├─ Code.json
│  │  │  │  │        ├─ Code.tsx
│  │  │  │  │        ├─ End.json
│  │  │  │  │        ├─ End.tsx
│  │  │  │  │        ├─ Home.json
│  │  │  │  │        ├─ Home.tsx
│  │  │  │  │        ├─ Http.json
│  │  │  │  │        ├─ Http.tsx
│  │  │  │  │        ├─ IfElse.json
│  │  │  │  │        ├─ IfElse.tsx
│  │  │  │  │        ├─ index.ts
│  │  │  │  │        ├─ Iteration.json
│  │  │  │  │        ├─ Iteration.tsx
│  │  │  │  │        ├─ IterationStart.json
│  │  │  │  │        ├─ IterationStart.tsx
│  │  │  │  │        ├─ Jinja.json
│  │  │  │  │        ├─ Jinja.tsx
│  │  │  │  │        ├─ KnowledgeRetrieval.json
│  │  │  │  │        ├─ KnowledgeRetrieval.tsx
│  │  │  │  │        ├─ Llm.json
│  │  │  │  │        ├─ Llm.tsx
│  │  │  │  │        ├─ ParameterExtractor.json
│  │  │  │  │        ├─ ParameterExtractor.tsx
│  │  │  │  │        ├─ ParameterPasser.json
│  │  │  │  │        ├─ ParameterPasser.tsx
│  │  │  │  │        ├─ QuestionClassifier.json
│  │  │  │  │        ├─ QuestionClassifier.tsx
│  │  │  │  │        ├─ RAGNode.json
│  │  │  │  │        ├─ RAGNode.tsx
│  │  │  │  │        ├─ TemplatingTransform.json
│  │  │  │  │        ├─ TemplatingTransform.tsx
│  │  │  │  │        ├─ VariableX.json
│  │  │  │  │        └─ VariableX.tsx
│  │  │  │  └─ utils.ts
│  │  │  ├─ image-gallery
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ image-uploader
│  │  │  │  ├─ chat-image-uploader.tsx
│  │  │  │  ├─ hooks.ts
│  │  │  │  ├─ image-link-input.tsx
│  │  │  │  ├─ image-list.tsx
│  │  │  │  ├─ image-preview.tsx
│  │  │  │  ├─ text-generation-image-uploader.tsx
│  │  │  │  ├─ uploader.tsx
│  │  │  │  └─ utils.ts
│  │  │  ├─ input
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ loading
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.css
│  │  │  ├─ logo
│  │  │  │  ├─ logo-embeded-chat-avatar.tsx
│  │  │  │  ├─ logo-embeded-chat-header.tsx
│  │  │  │  └─ logo-site.tsx
│  │  │  ├─ markdown.tsx
│  │  │  ├─ mermaid
│  │  │  │  └─ index.tsx
│  │  │  ├─ message-log-modal
│  │  │  │  └─ index.tsx
│  │  │  ├─ modal
│  │  │  │  ├─ delete-confirm-modal
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ index.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ notion-icon
│  │  │  │  ├─ index.module.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ notion-page-selector
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ clear.svg
│  │  │  │  │  ├─ down-arrow.svg
│  │  │  │  │  ├─ notion-empty-page.svg
│  │  │  │  │  ├─ notion-page.svg
│  │  │  │  │  ├─ search.svg
│  │  │  │  │  └─ setting.svg
│  │  │  │  ├─ base.module.css
│  │  │  │  ├─ base.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ notion-page-selector-modal
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ page-selector
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ search-input
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  └─ workspace-selector
│  │  │  │     ├─ index.module.css
│  │  │  │     └─ index.tsx
│  │  │  ├─ pagination
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ param-item
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ score-threshold-item.tsx
│  │  │  │  └─ top-k-item.tsx
│  │  │  ├─ popover
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ portal-to-follow-elem
│  │  │  │  └─ index.tsx
│  │  │  ├─ progress-bar
│  │  │  │  └─ index.tsx
│  │  │  ├─ prompt-editor
│  │  │  │  ├─ constants.tsx
│  │  │  │  ├─ hooks.ts
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ plugins
│  │  │  │  │  ├─ component-picker-block
│  │  │  │  │  │  ├─ hooks.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ menu.tsx
│  │  │  │  │  │  ├─ prompt-option.tsx
│  │  │  │  │  │  └─ variable-option.tsx
│  │  │  │  │  ├─ context-block
│  │  │  │  │  │  ├─ component.tsx
│  │  │  │  │  │  ├─ context-block-replacement-block.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ node.tsx
│  │  │  │  │  ├─ custom-text
│  │  │  │  │  │  └─ node.tsx
│  │  │  │  │  ├─ history-block
│  │  │  │  │  │  ├─ component.tsx
│  │  │  │  │  │  ├─ history-block-replacement-block.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ node.tsx
│  │  │  │  │  ├─ on-blur-or-focus-block.tsx
│  │  │  │  │  ├─ placeholder.tsx
│  │  │  │  │  ├─ query-block
│  │  │  │  │  │  ├─ component.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ node.tsx
│  │  │  │  │  │  └─ query-block-replacement-block.tsx
│  │  │  │  │  ├─ tree-view.tsx
│  │  │  │  │  ├─ update-block.tsx
│  │  │  │  │  ├─ variable-block
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ variable-value-block
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ node.tsx
│  │  │  │  │  │  └─ utils.ts
│  │  │  │  │  └─ workflow-variable-block
│  │  │  │  │     ├─ component.tsx
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     ├─ node.tsx
│  │  │  │  │     └─ workflow-variable-block-replacement-block.tsx
│  │  │  │  ├─ types.ts
│  │  │  │  └─ utils.ts
│  │  │  ├─ prompt-log-modal
│  │  │  │  ├─ card.tsx
│  │  │  │  └─ index.tsx
│  │  │  ├─ qrcode
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ radio
│  │  │  │  ├─ component
│  │  │  │  │  ├─ group
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ radio
│  │  │  │  │     └─ index.tsx
│  │  │  │  ├─ context
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  └─ ui.tsx
│  │  │  ├─ radio-card
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ simple
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  └─ style.module.css
│  │  │  ├─ retry-button
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ search-input
│  │  │  │  └─ index.tsx
│  │  │  ├─ select
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ locale.tsx
│  │  │  ├─ simple-pie-chart
│  │  │  │  ├─ index.module.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ slider
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.css
│  │  │  ├─ spinner
│  │  │  │  └─ index.tsx
│  │  │  ├─ svg
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ switch
│  │  │  │  └─ index.tsx
│  │  │  ├─ tab-header
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ tab-slider
│  │  │  │  └─ index.tsx
│  │  │  ├─ tab-slider-new
│  │  │  │  └─ index.tsx
│  │  │  ├─ tab-slider-plain
│  │  │  │  └─ index.tsx
│  │  │  ├─ tag
│  │  │  │  └─ index.tsx
│  │  │  ├─ tag-input
│  │  │  │  └─ index.tsx
│  │  │  ├─ tag-management
│  │  │  │  ├─ constant.ts
│  │  │  │  ├─ filter.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ selector.tsx
│  │  │  │  ├─ store.ts
│  │  │  │  ├─ style.module.css
│  │  │  │  ├─ tag-item-editor.tsx
│  │  │  │  └─ tag-remove-modal.tsx
│  │  │  ├─ text-generation
│  │  │  │  ├─ hooks.ts
│  │  │  │  └─ types.ts
│  │  │  ├─ toast
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ tooltip
│  │  │  │  └─ index.tsx
│  │  │  ├─ tooltip-plus
│  │  │  │  └─ index.tsx
│  │  │  ├─ topbar
│  │  │  │  └─ index.tsx
│  │  │  └─ voice-input
│  │  │     ├─ index.module.css
│  │  │     ├─ index.tsx
│  │  │     └─ utils.ts
│  │  ├─ billing
│  │  │  ├─ annotation-full
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ modal.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  └─ usage.tsx
│  │  │  ├─ apps-full
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ apps-full-in-dialog
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ billing-page
│  │  │  │  └─ index.tsx
│  │  │  ├─ config.ts
│  │  │  ├─ header-billing-btn
│  │  │  │  └─ index.tsx
│  │  │  ├─ plan
│  │  │  │  └─ index.tsx
│  │  │  ├─ pricing
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ plan-item.tsx
│  │  │  │  └─ select-plan-range.tsx
│  │  │  ├─ priority-label
│  │  │  │  └─ index.tsx
│  │  │  ├─ progress-bar
│  │  │  │  └─ index.tsx
│  │  │  ├─ type.ts
│  │  │  ├─ upgrade-btn
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ usage-info
│  │  │  │  ├─ apps-info.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ vector-space-info.tsx
│  │  │  ├─ utils
│  │  │  │  └─ index.ts
│  │  │  └─ vector-space-full
│  │  │     ├─ index.tsx
│  │  │     └─ style.module.css
│  │  ├─ browser-initor.tsx
│  │  ├─ custom
│  │  │  ├─ custom-app-header-brand
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ custom-page
│  │  │  │  └─ index.tsx
│  │  │  ├─ custom-web-app-brand
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  └─ style.module.css
│  │  ├─ datasets
│  │  │  ├─ api
│  │  │  │  └─ index.tsx
│  │  │  ├─ common
│  │  │  │  ├─ check-rerank-model.ts
│  │  │  │  ├─ economical-retrieval-method-config
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ retrieval-method-config
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ retrieval-method-info
│  │  │  │  │  └─ index.tsx
│  │  │  │  └─ retrieval-param-config
│  │  │  │     └─ index.tsx
│  │  │  ├─ create
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ alert-triangle.svg
│  │  │  │  │  ├─ annotation-info.svg
│  │  │  │  │  ├─ arrow-narrow-left.svg
│  │  │  │  │  ├─ book-open-01.svg
│  │  │  │  │  ├─ check.svg
│  │  │  │  │  ├─ close.svg
│  │  │  │  │  ├─ csv.svg
│  │  │  │  │  ├─ doc.svg
│  │  │  │  │  ├─ docx.svg
│  │  │  │  │  ├─ file.svg
│  │  │  │  │  ├─ folder-plus.svg
│  │  │  │  │  ├─ html.svg
│  │  │  │  │  ├─ Icon-3-dots.svg
│  │  │  │  │  ├─ json.svg
│  │  │  │  │  ├─ Loading.svg
│  │  │  │  │  ├─ md.svg
│  │  │  │  │  ├─ normal.svg
│  │  │  │  │  ├─ notion.svg
│  │  │  │  │  ├─ pdf.svg
│  │  │  │  │  ├─ piggy-bank-01.svg
│  │  │  │  │  ├─ sliders-02.svg
│  │  │  │  │  ├─ star-07.svg
│  │  │  │  │  ├─ star.svg
│  │  │  │  │  ├─ trash.svg
│  │  │  │  │  ├─ txt.svg
│  │  │  │  │  ├─ unknow.svg
│  │  │  │  │  ├─ upload-cloud-01.svg
│  │  │  │  │  ├─ web.svg
│  │  │  │  │  ├─ xlsx.svg
│  │  │  │  │  └─ zap-fast.svg
│  │  │  │  ├─ embedding-process
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ empty-dataset-creation-modal
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ file-preview
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ file-uploader
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ index.module.css
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ notion-page-preview
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ step-one
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ step-three
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ step-two
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ language-select
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ preview-item
│  │  │  │  │     └─ index.tsx
│  │  │  │  ├─ steps-nav-bar
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ stop-embedding-modal
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  └─ website
│  │  │  │     ├─ firecrawl
│  │  │  │     │  ├─ base
│  │  │  │     │  │  ├─ checkbox-with-label.tsx
│  │  │  │     │  │  ├─ error-message.tsx
│  │  │  │     │  │  ├─ field.tsx
│  │  │  │     │  │  ├─ input.tsx
│  │  │  │     │  │  ├─ options-wrap.tsx
│  │  │  │     │  │  └─ url-input.tsx
│  │  │  │     │  ├─ crawled-result-item.tsx
│  │  │  │     │  ├─ crawled-result.tsx
│  │  │  │     │  ├─ crawling.tsx
│  │  │  │     │  ├─ header.tsx
│  │  │  │     │  ├─ index.tsx
│  │  │  │     │  ├─ mock-crawl-result.ts
│  │  │  │     │  └─ options.tsx
│  │  │  │     ├─ index.tsx
│  │  │  │     ├─ no-data.tsx
│  │  │  │     └─ preview.tsx
│  │  │  ├─ documents
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ atSign.svg
│  │  │  │  │  ├─ bezierCurve.svg
│  │  │  │  │  ├─ bookOpen.svg
│  │  │  │  │  ├─ briefcase.svg
│  │  │  │  │  ├─ cardLoading.svg
│  │  │  │  │  ├─ file.svg
│  │  │  │  │  ├─ globe.svg
│  │  │  │  │  ├─ graduationHat.svg
│  │  │  │  │  ├─ hitLoading.svg
│  │  │  │  │  ├─ layoutRightClose.svg
│  │  │  │  │  ├─ layoutRightShow.svg
│  │  │  │  │  ├─ messageTextCircle.svg
│  │  │  │  │  ├─ normal.svg
│  │  │  │  │  ├─ star.svg
│  │  │  │  │  ├─ target.svg
│  │  │  │  │  └─ typeSquare.svg
│  │  │  │  ├─ detail
│  │  │  │  │  ├─ batch-modal
│  │  │  │  │  │  ├─ csv-downloader.tsx
│  │  │  │  │  │  ├─ csv-uploader.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ completed
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ InfiniteVirtualList.tsx
│  │  │  │  │  │  ├─ SegmentCard.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ embedding
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ metadata
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ new-segment-modal.tsx
│  │  │  │  │  ├─ segment-add
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ settings
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ style.module.css
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ list.tsx
│  │  │  │  ├─ rename-modal.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ hit-testing
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ clock.svg
│  │  │  │  │  ├─ grid.svg
│  │  │  │  │  └─ plugin.svg
│  │  │  │  ├─ hit-detail.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ modify-retrieval-modal.tsx
│  │  │  │  ├─ style.module.css
│  │  │  │  └─ textarea.tsx
│  │  │  ├─ rename-modal
│  │  │  │  └─ index.tsx
│  │  │  └─ settings
│  │  │     ├─ form
│  │  │     │  └─ index.tsx
│  │  │     ├─ index-method-radio
│  │  │     │  ├─ assets
│  │  │     │  │  ├─ economy.svg
│  │  │     │  │  └─ high-quality.svg
│  │  │     │  ├─ index.module.css
│  │  │     │  └─ index.tsx
│  │  │     └─ permissions-radio
│  │  │        ├─ assets
│  │  │        │  └─ user.svg
│  │  │        ├─ index.module.css
│  │  │        └─ index.tsx
│  │  ├─ develop
│  │  │  ├─ code.tsx
│  │  │  ├─ doc.tsx
│  │  │  ├─ index.tsx
│  │  │  ├─ md.tsx
│  │  │  ├─ secret-key
│  │  │  │  ├─ assets
│  │  │  │  │  ├─ copied.svg
│  │  │  │  │  ├─ copy-hover.svg
│  │  │  │  │  ├─ copy.svg
│  │  │  │  │  ├─ pause.svg
│  │  │  │  │  ├─ play.svg
│  │  │  │  │  ├─ qrcode-hover.svg
│  │  │  │  │  ├─ qrcode.svg
│  │  │  │  │  ├─ svg.svg
│  │  │  │  │  ├─ svged.svg
│  │  │  │  │  ├─ trash-gray.svg
│  │  │  │  │  └─ trash-red.svg
│  │  │  │  ├─ input-copy.tsx
│  │  │  │  ├─ secret-key-button.tsx
│  │  │  │  ├─ secret-key-generate.tsx
│  │  │  │  ├─ secret-key-modal.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ tag.tsx
│  │  │  └─ template
│  │  │     ├─ template.en.mdx
│  │  │     ├─ template.zh.mdx
│  │  │     ├─ template_advanced_chat.en.mdx
│  │  │     ├─ template_advanced_chat.zh.mdx
│  │  │     ├─ template_chat.en.mdx
│  │  │     ├─ template_chat.zh.mdx
│  │  │     ├─ template_workflow.en.mdx
│  │  │     └─ template_workflow.zh.mdx
│  │  ├─ explore
│  │  │  ├─ app-card
│  │  │  │  └─ index.tsx
│  │  │  ├─ app-list
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  ├─ category.tsx
│  │  │  ├─ create-app-modal
│  │  │  │  └─ index.tsx
│  │  │  ├─ index.tsx
│  │  │  ├─ installed-app
│  │  │  │  └─ index.tsx
│  │  │  ├─ item-operation
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  └─ sidebar
│  │  │     ├─ app-nav-item
│  │  │     │  ├─ index.tsx
│  │  │     │  └─ style.module.css
│  │  │     └─ index.tsx
│  │  ├─ header
│  │  │  ├─ account-about
│  │  │  │  ├─ index.module.css
│  │  │  │  └─ index.tsx
│  │  │  ├─ account-dropdown
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ workplace-selector
│  │  │  │     ├─ index.module.css
│  │  │  │     └─ index.tsx
│  │  │  ├─ account-setting
│  │  │  │  ├─ account-page
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ api-based-extension-page
│  │  │  │  │  ├─ empty.tsx
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ item.tsx
│  │  │  │  │  ├─ modal.tsx
│  │  │  │  │  └─ selector.tsx
│  │  │  │  ├─ collapse
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ data-source-page
│  │  │  │  │  ├─ data-source-notion
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ operate
│  │  │  │  │  │     └─ index.tsx
│  │  │  │  │  ├─ data-source-website
│  │  │  │  │  │  ├─ config-firecrawl-modal.tsx
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ panel
│  │  │  │  │     ├─ config-item.tsx
│  │  │  │  │     ├─ index.tsx
│  │  │  │  │     ├─ style.module.css
│  │  │  │  │     └─ types.ts
│  │  │  │  ├─ index.module.css
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ Integrations-page
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ key-validator
│  │  │  │  │  ├─ declarations.ts
│  │  │  │  │  ├─ hooks.ts
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ KeyInput.tsx
│  │  │  │  │  ├─ Operate.tsx
│  │  │  │  │  └─ ValidateStatus.tsx
│  │  │  │  ├─ language-page
│  │  │  │  │  ├─ index.module.css
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ members-page
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ invite-modal
│  │  │  │  │  │  ├─ index.module.css
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ invited-modal
│  │  │  │  │  │  ├─ assets
│  │  │  │  │  │  │  ├─ copied.svg
│  │  │  │  │  │  │  ├─ copy-hover.svg
│  │  │  │  │  │  │  └─ copy.svg
│  │  │  │  │  │  ├─ index.module.css
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ invitation-link.tsx
│  │  │  │  │  └─ operation
│  │  │  │  │     ├─ index.module.css
│  │  │  │  │     └─ index.tsx
│  │  │  │  ├─ model-provider-page
│  │  │  │  │  ├─ declarations.ts
│  │  │  │  │  ├─ hooks.ts
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  ├─ model-badge
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ model-icon
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ model-modal
│  │  │  │  │  │  ├─ Form.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ Input.tsx
│  │  │  │  │  │  └─ model-load-balancing-entry-modal.tsx
│  │  │  │  │  ├─ model-name
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ model-parameter-modal
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ parameter-item.tsx
│  │  │  │  │  │  ├─ presets-parameter.tsx
│  │  │  │  │  │  ├─ stop-sequence.tsx
│  │  │  │  │  │  └─ trigger.tsx
│  │  │  │  │  ├─ model-selector
│  │  │  │  │  │  ├─ deprecated-model-trigger.tsx
│  │  │  │  │  │  ├─ empty-trigger.tsx
│  │  │  │  │  │  ├─ feature-icon.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ model-trigger.tsx
│  │  │  │  │  │  ├─ popup-item.tsx
│  │  │  │  │  │  ├─ popup.tsx
│  │  │  │  │  │  └─ rerank-trigger.tsx
│  │  │  │  │  ├─ provider-added-card
│  │  │  │  │  │  ├─ add-model-button.tsx
│  │  │  │  │  │  ├─ cooldown-timer.tsx
│  │  │  │  │  │  ├─ credential-panel.tsx
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  ├─ model-list-item.tsx
│  │  │  │  │  │  ├─ model-list.tsx
│  │  │  │  │  │  ├─ model-load-balancing-configs.tsx
│  │  │  │  │  │  ├─ model-load-balancing-modal.tsx
│  │  │  │  │  │  ├─ priority-selector.tsx
│  │  │  │  │  │  ├─ priority-use-tip.tsx
│  │  │  │  │  │  ├─ quota-panel.tsx
│  │  │  │  │  │  └─ tab.tsx
│  │  │  │  │  ├─ provider-card
│  │  │  │  │  │  ├─ index.module.css
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ provider-icon
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ system-model-selector
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  └─ utils.ts
│  │  │  │  └─ plugin-page
│  │  │  │     ├─ index.tsx
│  │  │  │     ├─ SerpapiPlugin.tsx
│  │  │  │     └─ utils.ts
│  │  │  ├─ app-back
│  │  │  │  └─ index.tsx
│  │  │  ├─ app-nav
│  │  │  │  └─ index.tsx
│  │  │  ├─ app-selector
│  │  │  │  └─ index.tsx
│  │  │  ├─ assets
│  │  │  │  ├─ alpha.svg
│  │  │  │  ├─ anthropic.svg
│  │  │  │  ├─ azure.svg
│  │  │  │  ├─ bitbucket.svg
│  │  │  │  ├─ file.svg
│  │  │  │  ├─ github.svg
│  │  │  │  ├─ google.svg
│  │  │  │  ├─ gpt.svg
│  │  │  │  ├─ hugging-face.svg
│  │  │  │  ├─ notion.svg
│  │  │  │  ├─ salesforce.svg
│  │  │  │  ├─ serpapi.png
│  │  │  │  ├─ sync.svg
│  │  │  │  ├─ trash.svg
│  │  │  │  └─ twitter.svg
│  │  │  ├─ dataset-nav
│  │  │  │  └─ index.tsx
│  │  │  ├─ env-nav
│  │  │  │  └─ index.tsx
│  │  │  ├─ explore-nav
│  │  │  │  └─ index.tsx
│  │  │  ├─ github-star
│  │  │  │  └─ index.tsx
│  │  │  ├─ HeaderWrapper.tsx
│  │  │  ├─ index.module.css
│  │  │  ├─ index.tsx
│  │  │  ├─ indicator
│  │  │  │  └─ index.tsx
│  │  │  ├─ maintenance-notice.tsx
│  │  │  ├─ nav
│  │  │  │  ├─ index.module.css
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ nav-selector
│  │  │  │     └─ index.tsx
│  │  │  └─ tools-nav
│  │  │     └─ index.tsx
│  │  ├─ i18n-server.tsx
│  │  ├─ i18n.tsx
│  │  ├─ sentry-initor.tsx
│  │  ├─ share
│  │  │  ├─ text-generation
│  │  │  │  ├─ icons
│  │  │  │  │  └─ star.svg
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ no-data
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ result
│  │  │  │  │  ├─ content.tsx
│  │  │  │  │  ├─ header.tsx
│  │  │  │  │  └─ index.tsx
│  │  │  │  ├─ run-batch
│  │  │  │  │  ├─ csv-download
│  │  │  │  │  │  └─ index.tsx
│  │  │  │  │  ├─ csv-reader
│  │  │  │  │  │  ├─ index.tsx
│  │  │  │  │  │  └─ style.module.css
│  │  │  │  │  ├─ index.tsx
│  │  │  │  │  └─ res-download
│  │  │  │  │     └─ index.tsx
│  │  │  │  ├─ run-once
│  │  │  │  │  └─ index.tsx
│  │  │  │  └─ style.module.css
│  │  │  └─ utils.ts
│  │  ├─ swr-initor.tsx
│  │  ├─ tools
│  │  │  ├─ add-tool-modal
│  │  │  │  ├─ category.tsx
│  │  │  │  ├─ D.png
│  │  │  │  ├─ empty.png
│  │  │  │  ├─ empty.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  ├─ tools.tsx
│  │  │  │  └─ type.tsx
│  │  │  ├─ create-var
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ select-var-type.tsx
│  │  │  ├─ edit-custom-collection-modal
│  │  │  │  ├─ config-credentials.tsx
│  │  │  │  ├─ examples.ts
│  │  │  │  ├─ get-schema.tsx
│  │  │  │  ├─ index.tsx
│  │  │  │  └─ test-api.tsx
│  │  │  ├─ labels
│  │  │  │  ├─ constant.ts
│  │  │  │  ├─ filter.tsx
│  │  │  │  ├─ selector.tsx
│  │  │  │  └─ store.ts
│  │  │  ├─ provider
│  │  │  │  ├─ card.tsx
│  │  │  │  ├─ contribute.tsx
│  │  │  │  ├─ custom-create-card.tsx
│  │  │  │  ├─ detail.tsx
│  │  │  │  ├─ grid_bg.svg
│  │  │  │  └─ tool-item.tsx
│  │  │  ├─ provider-list.tsx
│  │  │  ├─ setting
│  │  │  ├─ types.ts
│  │  │  ├─ utils
│  │  │  │  ├─ index.ts
│  │  │  │  └─ to-form-schema.ts
│  │  │  └─ workflow-tool
│  │  │     ├─ configure-button.tsx
│  │  │     ├─ confirm-modal
│  │  │     │  ├─ index.tsx
│  │  │     │  └─ style.module.css
│  │  │     ├─ index.tsx
│  │  │     └─ method-selector.tsx
│  │  ├─ with-i18n.tsx
│  │  └─ workflow
│  │     ├─ block-icon.tsx
│  │     ├─ block-selector
│  │     │  ├─ all-tools.tsx
│  │     │  ├─ blocks.tsx
│  │     │  ├─ constants.tsx
│  │     │  ├─ hooks.ts
│  │     │  ├─ index-bar.tsx
│  │     │  ├─ index.tsx
│  │     │  ├─ tabs.tsx
│  │     │  ├─ tools.tsx
│  │     │  └─ types.ts
│  │     ├─ candidate-node.tsx
│  │     ├─ constants.ts
│  │     ├─ context.tsx
│  │     ├─ custom-connection-line.tsx
│  │     ├─ custom-edge.tsx
│  │     ├─ dsl-export-confirm-modal.tsx
│  │     ├─ features.tsx
│  │     ├─ header
│  │     │  ├─ checklist.tsx
│  │     │  ├─ editing-title.tsx
│  │     │  ├─ env-button.tsx
│  │     │  ├─ index.tsx
│  │     │  ├─ restoring-title.tsx
│  │     │  ├─ run-and-history.tsx
│  │     │  ├─ running-title.tsx
│  │     │  ├─ undo-redo.tsx
│  │     │  ├─ view-history.tsx
│  │     │  └─ view-workflow-history.tsx
│  │     ├─ help-line
│  │     │  ├─ index.tsx
│  │     │  └─ types.ts
│  │     ├─ hooks
│  │     │  ├─ index.ts
│  │     │  ├─ use-checklist.ts
│  │     │  ├─ use-edges-interactions.ts
│  │     │  ├─ use-helpline.ts
│  │     │  ├─ use-node-data-update.ts
│  │     │  ├─ use-nodes-data.ts
│  │     │  ├─ use-nodes-interactions.ts
│  │     │  ├─ use-nodes-layout.ts
│  │     │  ├─ use-nodes-sync-draft.ts
│  │     │  ├─ use-panel-interactions.ts
│  │     │  ├─ use-selection-interactions.ts
│  │     │  ├─ use-workflow-history.ts
│  │     │  ├─ use-workflow-interactions.ts
│  │     │  ├─ use-workflow-mode.ts
│  │     │  ├─ use-workflow-run.ts
│  │     │  ├─ use-workflow-start-run.tsx
│  │     │  ├─ use-workflow-template.ts
│  │     │  ├─ use-workflow-variables.ts
│  │     │  └─ use-workflow.ts
│  │     ├─ index.tsx
│  │     ├─ node-contextmenu.tsx
│  │     ├─ nodes
│  │     │  ├─ agent-node
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ answer
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ code
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ dependency-picker.tsx
│  │     │  │  ├─ dependency.tsx
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ constants.ts
│  │     │  ├─ end
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ http
│  │     │  │  ├─ components
│  │     │  │  │  ├─ api-input.tsx
│  │     │  │  │  ├─ authorization
│  │     │  │  │  │  ├─ index.tsx
│  │     │  │  │  │  └─ radio-group.tsx
│  │     │  │  │  ├─ edit-body
│  │     │  │  │  │  └─ index.tsx
│  │     │  │  │  ├─ key-value
│  │     │  │  │  │  ├─ bulk-edit
│  │     │  │  │  │  │  └─ index.tsx
│  │     │  │  │  │  ├─ index.tsx
│  │     │  │  │  │  └─ key-value-edit
│  │     │  │  │  │     ├─ index.tsx
│  │     │  │  │  │     ├─ input-item.tsx
│  │     │  │  │  │     └─ item.tsx
│  │     │  │  │  └─ timeout
│  │     │  │  │     └─ index.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ hooks
│  │     │  │  │  └─ use-key-value-list.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ if-else
│  │     │  │  ├─ components
│  │     │  │  │  ├─ condition-add.tsx
│  │     │  │  │  ├─ condition-list
│  │     │  │  │  │  ├─ condition-input.tsx
│  │     │  │  │  │  ├─ condition-item.tsx
│  │     │  │  │  │  ├─ condition-operator.tsx
│  │     │  │  │  │  └─ index.tsx
│  │     │  │  │  ├─ condition-number-input.tsx
│  │     │  │  │  └─ condition-value.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ index.tsx
│  │     │  ├─ iteration
│  │     │  │  ├─ add-block.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ insert-block.tsx
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ use-interactions.ts
│  │     │  ├─ knowledge-retrieval
│  │     │  │  ├─ components
│  │     │  │  │  ├─ add-dataset.tsx
│  │     │  │  │  ├─ dataset-item.tsx
│  │     │  │  │  ├─ dataset-list.tsx
│  │     │  │  │  └─ retrieval-config.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ llm
│  │     │  │  ├─ components
│  │     │  │  │  ├─ config-prompt-item.tsx
│  │     │  │  │  ├─ config-prompt.tsx
│  │     │  │  │  └─ resolution-picker.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ parameter-extractor
│  │     │  │  ├─ components
│  │     │  │  │  ├─ extract-parameter
│  │     │  │  │  │  ├─ import-from-tool.tsx
│  │     │  │  │  │  ├─ item.tsx
│  │     │  │  │  │  ├─ list.tsx
│  │     │  │  │  │  └─ update.tsx
│  │     │  │  │  └─ reasoning-mode-picker.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  └─ use-config.ts
│  │     │  ├─ parameter-passer
│  │     │  │  ├─ components
│  │     │  │  │  ├─ add-variable
│  │     │  │  │  │  └─ index.tsx
│  │     │  │  │  ├─ node-group-item.tsx
│  │     │  │  │  ├─ node-variable-item.tsx
│  │     │  │  │  ├─ var-group-item.tsx
│  │     │  │  │  └─ var-list
│  │     │  │  │     ├─ index.tsx
│  │     │  │  │     └─ use-var-list.ts
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ hooks.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ question-classifier
│  │     │  │  ├─ components
│  │     │  │  │  ├─ advanced-setting.tsx
│  │     │  │  │  ├─ class-item.tsx
│  │     │  │  │  └─ class-list.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ rag-node
│  │     │  │  ├─ components
│  │     │  │  │  ├─ editor.tsx
│  │     │  │  │  ├─ field.tsx
│  │     │  │  │  └─ var-list.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ start
│  │     │  │  ├─ components
│  │     │  │  │  ├─ var-item.tsx
│  │     │  │  │  └─ var-list.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ template-transform
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ tool
│  │     │  │  ├─ components
│  │     │  │  │  └─ input-var-list.tsx
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  ├─ variable-assigner
│  │     │  │  ├─ components
│  │     │  │  │  ├─ add-variable
│  │     │  │  │  │  └─ index.tsx
│  │     │  │  │  ├─ node-group-item.tsx
│  │     │  │  │  ├─ node-variable-item.tsx
│  │     │  │  │  ├─ var-group-item.tsx
│  │     │  │  │  └─ var-list
│  │     │  │  │     ├─ index.tsx
│  │     │  │  │     └─ use-var-list.ts
│  │     │  │  ├─ default.ts
│  │     │  │  ├─ hooks.ts
│  │     │  │  ├─ node.tsx
│  │     │  │  ├─ panel.tsx
│  │     │  │  ├─ types.ts
│  │     │  │  ├─ use-config.ts
│  │     │  │  └─ utils.ts
│  │     │  └─ _base
│  │     │     ├─ components
│  │     │     │  ├─ add-button.tsx
│  │     │     │  ├─ add-variable-popup-with-position.tsx
│  │     │     │  ├─ add-variable-popup.tsx
│  │     │     │  ├─ before-run-form
│  │     │     │  │  ├─ form-item.tsx
│  │     │     │  │  ├─ form.tsx
│  │     │     │  │  └─ index.tsx
│  │     │     │  ├─ editor
│  │     │     │  │  ├─ base.tsx
│  │     │     │  │  ├─ code-editor
│  │     │     │  │  │  ├─ editor-support-vars.tsx
│  │     │     │  │  │  ├─ index.tsx
│  │     │     │  │  │  └─ style.css
│  │     │     │  │  ├─ text-editor.tsx
│  │     │     │  │  └─ wrap.tsx
│  │     │     │  ├─ field.tsx
│  │     │     │  ├─ help-link.tsx
│  │     │     │  ├─ info-panel.tsx
│  │     │     │  ├─ input-support-select-var.tsx
│  │     │     │  ├─ input-var-type-icon.tsx
│  │     │     │  ├─ list-no-data-placeholder.tsx
│  │     │     │  ├─ memory-config.tsx
│  │     │     │  ├─ next-step
│  │     │     │  │  ├─ add.tsx
│  │     │     │  │  ├─ index.tsx
│  │     │     │  │  ├─ item.tsx
│  │     │     │  │  └─ line.tsx
│  │     │     │  ├─ node-control.tsx
│  │     │     │  ├─ node-handle.tsx
│  │     │     │  ├─ node-resizer.tsx
│  │     │     │  ├─ output-vars.tsx
│  │     │     │  ├─ panel-operator
│  │     │     │  │  ├─ change-block.tsx
│  │     │     │  │  ├─ index.tsx
│  │     │     │  │  └─ panel-operator-popup.tsx
│  │     │     │  ├─ prompt
│  │     │     │  │  └─ editor.tsx
│  │     │     │  ├─ readonly-input-with-select-var.tsx
│  │     │     │  ├─ remove-button.tsx
│  │     │     │  ├─ remove-effect-var-confirm.tsx
│  │     │     │  ├─ selector.tsx
│  │     │     │  ├─ split.tsx
│  │     │     │  ├─ support-var-input
│  │     │     │  │  └─ index.tsx
│  │     │     │  ├─ title-description-input.tsx
│  │     │     │  ├─ toggle-expand-btn.tsx
│  │     │     │  ├─ variable
│  │     │     │  │  ├─ output-var-list.tsx
│  │     │     │  │  ├─ utils.ts
│  │     │     │  │  ├─ var-list.tsx
│  │     │     │  │  ├─ var-reference-picker.tsx
│  │     │     │  │  ├─ var-reference-popup.tsx
│  │     │     │  │  ├─ var-reference-vars.tsx
│  │     │     │  │  └─ var-type-picker.tsx
│  │     │     │  └─ variable-tag.tsx
│  │     │     ├─ hooks
│  │     │     │  ├─ use-available-var-list.ts
│  │     │     │  ├─ use-node-crud.ts
│  │     │     │  ├─ use-node-help-link.ts
│  │     │     │  ├─ use-node-info.ts
│  │     │     │  ├─ use-one-step-run.ts
│  │     │     │  ├─ use-output-var-list.ts
│  │     │     │  ├─ use-resize-panel.ts
│  │     │     │  ├─ use-toggle-expend.ts
│  │     │     │  └─ use-var-list.ts
│  │     │     ├─ node.tsx
│  │     │     └─ panel.tsx
│  │     ├─ note-node
│  │     │  ├─ constants.ts
│  │     │  ├─ hooks.ts
│  │     │  ├─ index.tsx
│  │     │  ├─ note-editor
│  │     │  │  ├─ context.tsx
│  │     │  │  ├─ editor.tsx
│  │     │  │  ├─ index.tsx
│  │     │  │  ├─ plugins
│  │     │  │  │  ├─ format-detector-plugin
│  │     │  │  │  │  ├─ hooks.ts
│  │     │  │  │  │  └─ index.tsx
│  │     │  │  │  └─ link-editor-plugin
│  │     │  │  │     ├─ component.tsx
│  │     │  │  │     ├─ hooks.ts
│  │     │  │  │     └─ index.tsx
│  │     │  │  ├─ store.ts
│  │     │  │  ├─ theme
│  │     │  │  │  ├─ index.ts
│  │     │  │  │  └─ theme.css
│  │     │  │  ├─ toolbar
│  │     │  │  │  ├─ color-picker.tsx
│  │     │  │  │  ├─ command.tsx
│  │     │  │  │  ├─ divider.tsx
│  │     │  │  │  ├─ font-size-selector.tsx
│  │     │  │  │  ├─ hooks.ts
│  │     │  │  │  ├─ index.tsx
│  │     │  │  │  └─ operator.tsx
│  │     │  │  └─ utils.ts
│  │     │  └─ types.ts
│  │     ├─ operator
│  │     │  ├─ add-block.tsx
│  │     │  ├─ control.tsx
│  │     │  ├─ hooks.ts
│  │     │  ├─ index.tsx
│  │     │  ├─ tip-popup.tsx
│  │     │  └─ zoom-in-out.tsx
│  │     ├─ panel
│  │     │  ├─ chat-record
│  │     │  │  ├─ index.tsx
│  │     │  │  └─ user-input.tsx
│  │     │  ├─ debug-and-preview
│  │     │  │  ├─ chat-wrapper.tsx
│  │     │  │  ├─ empty.tsx
│  │     │  │  ├─ hooks.ts
│  │     │  │  ├─ index.tsx
│  │     │  │  └─ user-input.tsx
│  │     │  ├─ env-panel
│  │     │  │  ├─ index.tsx
│  │     │  │  ├─ variable-modal.tsx
│  │     │  │  └─ variable-trigger.tsx
│  │     │  ├─ index.tsx
│  │     │  ├─ inputs-panel.tsx
│  │     │  ├─ record.tsx
│  │     │  └─ workflow-preview.tsx
│  │     ├─ panel-contextmenu.tsx
│  │     ├─ run
│  │     │  ├─ index.tsx
│  │     │  ├─ iteration-result-panel.tsx
│  │     │  ├─ meta.tsx
│  │     │  ├─ node.tsx
│  │     │  ├─ output-panel.tsx
│  │     │  ├─ result-panel.tsx
│  │     │  ├─ result-text.tsx
│  │     │  ├─ status.tsx
│  │     │  └─ tracing-panel.tsx
│  │     ├─ shortcuts-name.tsx
│  │     ├─ store.ts
│  │     ├─ style.css
│  │     ├─ syncing-data-modal.tsx
│  │     ├─ types.ts
│  │     ├─ update-dsl-modal.tsx
│  │     ├─ utils.ts
│  │     └─ workflow-history-store.tsx
│  ├─ forgot-password
│  │  ├─ ChangePasswordForm.tsx
│  │  ├─ ForgotPasswordForm.tsx
│  │  └─ page.tsx
│  ├─ init
│  │  ├─ InitPasswordPopup.tsx
│  │  └─ page.tsx
│  ├─ install
│  │  ├─ installForm.tsx
│  │  └─ page.tsx
│  ├─ layout.tsx
│  ├─ page.module.css
│  ├─ page.tsx
│  ├─ signin
│  │  ├─ assets
│  │  │  ├─ background.png
│  │  │  ├─ github.svg
│  │  │  └─ google.svg
│  │  ├─ forms.tsx
│  │  ├─ normalForm.tsx
│  │  ├─ oneMoreStep.tsx
│  │  ├─ page.module.css
│  │  ├─ page.tsx
│  │  ├─ userSSOForm.tsx
│  │  └─ _header.tsx
│  └─ styles
│     ├─ globals.css
│     ├─ markdown.scss
│     └─ preflight.css
├─ assets
│  ├─ action.svg
│  ├─ csv.svg
│  ├─ delete.svg
│  ├─ doc.svg
│  ├─ docx.svg
│  ├─ html.svg
│  ├─ json.svg
│  ├─ md.svg
│  ├─ pdf.svg
│  ├─ txt.svg
│  └─ xlsx.svg
├─ bin
│  └─ uglify-embed.js
├─ config
│  └─ index.ts
├─ context
│  ├─ app-context.tsx
│  ├─ dataset-detail.ts
│  ├─ datasets-context.tsx
│  ├─ debug-configuration.ts
│  ├─ event-emitter.tsx
│  ├─ explore-context.ts
│  ├─ i18n.ts
│  ├─ modal-context.tsx
│  ├─ provider-context.tsx
│  └─ workspace-context.tsx
├─ docker
│  ├─ entrypoint.sh
│  └─ pm2.json
├─ Dockerfile
├─ global.d.ts
├─ hooks
│  ├─ use-breakpoints.ts
│  ├─ use-metadata.ts
│  ├─ use-moderate.ts
│  ├─ use-pay.tsx
│  ├─ use-tab-searchparams.ts
│  └─ use-timestamp.ts
├─ i18n
│  ├─ de-DE
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ en-US
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ es-ES
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ fr-FR
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ hi-IN
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ i18next-config.ts
│  ├─ index.ts
│  ├─ ja-JP
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ ko-KR
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ language.ts
│  ├─ languages.json
│  ├─ pl-PL
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ pt-BR
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ README.md
│  ├─ ro-RO
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ script.js
│  ├─ server.ts
│  ├─ uk-UA
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ vi-VN
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  ├─ zh-Hans
│  │  ├─ app-annotation.ts
│  │  ├─ app-api.ts
│  │  ├─ app-debug.ts
│  │  ├─ app-log.ts
│  │  ├─ app-overview.ts
│  │  ├─ app.ts
│  │  ├─ billing.ts
│  │  ├─ common.ts
│  │  ├─ custom.ts
│  │  ├─ dataset-creation.ts
│  │  ├─ dataset-documents.ts
│  │  ├─ dataset-hit-testing.ts
│  │  ├─ dataset-settings.ts
│  │  ├─ dataset.ts
│  │  ├─ explore.ts
│  │  ├─ layout.ts
│  │  ├─ login.ts
│  │  ├─ register.ts
│  │  ├─ run-log.ts
│  │  ├─ share-app.ts
│  │  ├─ tools.ts
│  │  └─ workflow.ts
│  └─ zh-Hant
│     ├─ app-annotation.ts
│     ├─ app-api.ts
│     ├─ app-debug.ts
│     ├─ app-log.ts
│     ├─ app-overview.ts
│     ├─ app.ts
│     ├─ billing.ts
│     ├─ common.ts
│     ├─ custom.ts
│     ├─ dataset-creation.ts
│     ├─ dataset-documents.ts
│     ├─ dataset-hit-testing.ts
│     ├─ dataset-settings.ts
│     ├─ dataset.ts
│     ├─ explore.ts
│     ├─ layout.ts
│     ├─ login.ts
│     ├─ register.ts
│     ├─ run-log.ts
│     ├─ share-app.ts
│     ├─ tools.ts
│     └─ workflow.ts
├─ layout
│  ├─ assets
│  │  ├─ back.png
│  │  └─ user.png
│  └─ Header.tsx
├─ models
│  ├─ app.ts
│  ├─ common.ts
│  ├─ datasets.ts
│  ├─ debug.ts
│  ├─ explore.ts
│  ├─ log.ts
│  ├─ share.ts
│  └─ user.ts
├─ next.config.js
├─ package.json
├─ postcss.config.js
├─ public
│  ├─ bg
│  │  ├─ agentBg1.png
│  │  ├─ agentBg2.png
│  │  ├─ agentBg3.png
│  │  ├─ agentChatBg1.png
│  │  ├─ agentChatBg2.png
│  │  ├─ agentChatBg3.png
│  │  ├─ agentChatBg4.png
│  │  ├─ agentChatBg5.png
│  │  ├─ allBanner.png
│  │  ├─ allBg.png
│  │  ├─ chatBg1.png
│  │  ├─ chatBg2.png
│  │  ├─ chatBg3.png
│  │  ├─ chatBg4.png
│  │  ├─ chatBg5.png
│  │  ├─ workflowBg1.png
│  │  ├─ workflowBg2.png
│  │  ├─ workflowBg3.png
│  │  ├─ workflowBg4.png
│  │  └─ workflowBg5.png
│  ├─ embed.js
│  ├─ embed.min.js
│  ├─ favicon.ico
│  ├─ image
│  │  ├─ add.png
│  │  ├─ back.png
│  │  ├─ bannerMap.png
│  │  ├─ circleIcon.png
│  │  ├─ editIcon.png
│  │  ├─ iconBook.png
│  │  ├─ rightGo.png
│  │  ├─ setEdit.png
│  │  └─ user.png
│  ├─ logo
│  │  ├─ logo-embeded-chat-avatar.png
│  │  ├─ logo-embeded-chat-header.png
│  │  └─ logo-site.png
│  └─ vs
│     ├─ base
│     │  ├─ browser
│     │  │  └─ ui
│     │  │     └─ codicons
│     │  │        └─ codicon
│     │  │           └─ codicon.ttf
│     │  ├─ common
│     │  │  └─ worker
│     │  │     ├─ simpleWorker.nls.de.js
│     │  │     ├─ simpleWorker.nls.es.js
│     │  │     ├─ simpleWorker.nls.fr.js
│     │  │     ├─ simpleWorker.nls.it.js
│     │  │     ├─ simpleWorker.nls.ja.js
│     │  │     ├─ simpleWorker.nls.js
│     │  │     ├─ simpleWorker.nls.ko.js
│     │  │     ├─ simpleWorker.nls.ru.js
│     │  │     ├─ simpleWorker.nls.zh-cn.js
│     │  │     └─ simpleWorker.nls.zh-tw.js
│     │  └─ worker
│     │     └─ workerMain.js
│     ├─ basic-languages
│     │  ├─ abap
│     │  │  └─ abap.js
│     │  ├─ apex
│     │  │  └─ apex.js
│     │  ├─ azcli
│     │  │  └─ azcli.js
│     │  ├─ bat
│     │  │  └─ bat.js
│     │  ├─ bicep
│     │  │  └─ bicep.js
│     │  ├─ cameligo
│     │  │  └─ cameligo.js
│     │  ├─ clojure
│     │  │  └─ clojure.js
│     │  ├─ coffee
│     │  │  └─ coffee.js
│     │  ├─ cpp
│     │  │  └─ cpp.js
│     │  ├─ csharp
│     │  │  └─ csharp.js
│     │  ├─ csp
│     │  │  └─ csp.js
│     │  ├─ css
│     │  │  └─ css.js
│     │  ├─ cypher
│     │  │  └─ cypher.js
│     │  ├─ dart
│     │  │  └─ dart.js
│     │  ├─ dockerfile
│     │  │  └─ dockerfile.js
│     │  ├─ ecl
│     │  │  └─ ecl.js
│     │  ├─ elixir
│     │  │  └─ elixir.js
│     │  ├─ flow9
│     │  │  └─ flow9.js
│     │  ├─ freemarker2
│     │  │  └─ freemarker2.js
│     │  ├─ fsharp
│     │  │  └─ fsharp.js
│     │  ├─ go
│     │  │  └─ go.js
│     │  ├─ graphql
│     │  │  └─ graphql.js
│     │  ├─ handlebars
│     │  │  └─ handlebars.js
│     │  ├─ hcl
│     │  │  └─ hcl.js
│     │  ├─ html
│     │  │  └─ html.js
│     │  ├─ ini
│     │  │  └─ ini.js
│     │  ├─ java
│     │  │  └─ java.js
│     │  ├─ javascript
│     │  │  └─ javascript.js
│     │  ├─ julia
│     │  │  └─ julia.js
│     │  ├─ kotlin
│     │  │  └─ kotlin.js
│     │  ├─ less
│     │  │  └─ less.js
│     │  ├─ lexon
│     │  │  └─ lexon.js
│     │  ├─ liquid
│     │  │  └─ liquid.js
│     │  ├─ lua
│     │  │  └─ lua.js
│     │  ├─ m3
│     │  │  └─ m3.js
│     │  ├─ markdown
│     │  │  └─ markdown.js
│     │  ├─ mdx
│     │  │  └─ mdx.js
│     │  ├─ mips
│     │  │  └─ mips.js
│     │  ├─ msdax
│     │  │  └─ msdax.js
│     │  ├─ mysql
│     │  │  └─ mysql.js
│     │  ├─ objective-c
│     │  │  └─ objective-c.js
│     │  ├─ pascal
│     │  │  └─ pascal.js
│     │  ├─ pascaligo
│     │  │  └─ pascaligo.js
│     │  ├─ perl
│     │  │  └─ perl.js
│     │  ├─ pgsql
│     │  │  └─ pgsql.js
│     │  ├─ php
│     │  │  └─ php.js
│     │  ├─ pla
│     │  │  └─ pla.js
│     │  ├─ postiats
│     │  │  └─ postiats.js
│     │  ├─ powerquery
│     │  │  └─ powerquery.js
│     │  ├─ powershell
│     │  │  └─ powershell.js
│     │  ├─ protobuf
│     │  │  └─ protobuf.js
│     │  ├─ pug
│     │  │  └─ pug.js
│     │  ├─ python
│     │  │  └─ python.js
│     │  ├─ qsharp
│     │  │  └─ qsharp.js
│     │  ├─ r
│     │  │  └─ r.js
│     │  ├─ razor
│     │  │  └─ razor.js
│     │  ├─ redis
│     │  │  └─ redis.js
│     │  ├─ redshift
│     │  │  └─ redshift.js
│     │  ├─ restructuredtext
│     │  │  └─ restructuredtext.js
│     │  ├─ ruby
│     │  │  └─ ruby.js
│     │  ├─ rust
│     │  │  └─ rust.js
│     │  ├─ sb
│     │  │  └─ sb.js
│     │  ├─ scala
│     │  │  └─ scala.js
│     │  ├─ scheme
│     │  │  └─ scheme.js
│     │  ├─ scss
│     │  │  └─ scss.js
│     │  ├─ shell
│     │  │  └─ shell.js
│     │  ├─ solidity
│     │  │  └─ solidity.js
│     │  ├─ sophia
│     │  │  └─ sophia.js
│     │  ├─ sparql
│     │  │  └─ sparql.js
│     │  ├─ sql
│     │  │  └─ sql.js
│     │  ├─ st
│     │  │  └─ st.js
│     │  ├─ swift
│     │  │  └─ swift.js
│     │  ├─ systemverilog
│     │  │  └─ systemverilog.js
│     │  ├─ tcl
│     │  │  └─ tcl.js
│     │  ├─ twig
│     │  │  └─ twig.js
│     │  ├─ typescript
│     │  │  └─ typescript.js
│     │  ├─ vb
│     │  │  └─ vb.js
│     │  ├─ wgsl
│     │  │  └─ wgsl.js
│     │  ├─ xml
│     │  │  └─ xml.js
│     │  └─ yaml
│     │     └─ yaml.js
│     ├─ editor
│     │  ├─ editor.main.css
│     │  ├─ editor.main.js
│     │  ├─ editor.main.nls.de.js
│     │  ├─ editor.main.nls.es.js
│     │  ├─ editor.main.nls.fr.js
│     │  ├─ editor.main.nls.it.js
│     │  ├─ editor.main.nls.ja.js
│     │  ├─ editor.main.nls.js
│     │  ├─ editor.main.nls.ko.js
│     │  ├─ editor.main.nls.ru.js
│     │  ├─ editor.main.nls.zh-cn.js
│     │  └─ editor.main.nls.zh-tw.js
│     ├─ language
│     │  ├─ css
│     │  │  ├─ cssMode.js
│     │  │  └─ cssWorker.js
│     │  ├─ html
│     │  │  ├─ htmlMode.js
│     │  │  └─ htmlWorker.js
│     │  ├─ json
│     │  │  ├─ jsonMode.js
│     │  │  └─ jsonWorker.js
│     │  └─ typescript
│     │     ├─ tsMode.js
│     │     └─ tsWorker.js
│     └─ loader.js
├─ README.md
├─ service
│  ├─ annotation.ts
│  ├─ apps.ts
│  ├─ base.ts
│  ├─ billing.ts
│  ├─ common.ts
│  ├─ datasets.ts
│  ├─ debug.ts
│  ├─ demo
│  │  └─ index.tsx
│  ├─ explore.ts
│  ├─ log.ts
│  ├─ share.ts
│  ├─ sso.ts
│  ├─ tag.ts
│  ├─ tools.ts
│  └─ workflow.ts
├─ tailwind.config.js
├─ themes
│  ├─ dark.css
│  ├─ light.css
│  └─ tailwind-theme-var-define.ts
├─ tsconfig.json
├─ types
│  ├─ app.ts
│  ├─ feature.ts
│  └─ workflow.ts
├─ typography.js
├─ utils
│  ├─ app-redirection.ts
│  ├─ classnames.ts
│  ├─ format.ts
│  ├─ index.ts
│  ├─ model-config.ts
│  ├─ timezone.json
│  ├─ timezone.ts
│  └─ var.ts
└─ yarn.lock

```
