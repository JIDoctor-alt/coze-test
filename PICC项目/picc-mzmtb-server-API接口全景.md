# PICC门诊慢特病业务服务 - API接口全景

> 📖 **相关文档**：[申报流程解析](picc-mzmtb-server-申报流程解析.md) · [数据模型解析](picc-mzmtb-server-数据模型解析.md) · [项目全貌](picc-mzmtb-server-项目全貌.md) · [处方与药店管理解析](picc-mzmtb-server-处方与药店管理解析.md)

**统计口径**: 105个API类, 894个接口

## 一、接口总览

| 业务域 | API类数 | 接口数 | 占比 |
|--------|---------|--------|------|
| 申报管理 | 30 | 435 | 48.7% |
| 数据统计 | 4 | 25 | 2.8% |
| 慢病卡管理 | 6 | 52 | 5.8% |
| 外部对接 | 7 | 27 | 3.0% |
| 审核管理 | 8 | 36 | 4.0% |
| 药店管理 | 10 | 38 | 4.3% |
| 系统管理 | 14 | 155 | 17.3% |
| 费用管理 | 7 | 32 | 3.6% |
| 工作流 | 2 | 7 | 0.8% |
| 处方管理 | 6 | 87 | 9.7% |
| **合计** | **105** | **894** | **100%** |


## 一、申报管理接口 (435个接口)

**模块前缀**: /queryFilingImportRecord 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **DocDeclareApi** | POST | /query/query | 查询申报列表 |
| | POST | /query/bookPhysical | 预约体检 |
| | POST | /query/nonArrivalPhysical | 未体检 |
| | POST | /query/uploadPhysicalFile | 上传体检报告 |
| | POST | /query/uploadPhysicalFileForBatch | 批量上传体检报告 |
| | POST | /query/export | 导出报表 |
| | POST | /query/queryUploadSucc | 查询上传成功列表 |
| | POST | /query/getPhyNote | 获取体检注意事项 |
| | POST | /query/giveUp | 放弃体检 |
| **MbDeclareApi** | POST | /MbDeclare/MbDeclare |  |
| | POST | /MbDeclare/query | 查询线下申报记录 |
| | POST | /MbDeclare/queryMeans | 查询申报材料 |
| | POST | /MbDeclare/queryWorkUnit | 查询服务窗口 |
| | POST | /MbDeclare/declare | 线下申报 |
| | POST | /MbDeclare/declareSL | 商洛线下申报 |
| | POST | /MbDeclare/declareDelete | 删除申报记录 |
| | POST | /MbDeclare/queryDetail | 删除申报记录 |
| | POST | /MbDeclare/declareUpdate | 查看详细申报记录 |
| | POST | /MbDeclare/queryIcdType | 线下申报修改 |
| | POST | /MbDeclare/queryDeclareStatusAll | 通过疾病类型获取疾病集合 |
| | POST | /MbDeclare/imageFiles | 获取系统中全部的申报状态 |
| | POST | /MbDeclare/dzImageFiles | 批量上传图片 |
| | POST | /MbDeclare/imageFilesSL | 商洛批量上传图片 |
| | POST | /MbDeclare/slCheck | 商洛批量上传图片 |
| | POST | /MbDeclare/bjYaYlCheck | 商洛医保资格校验 |
| | POST | /MbDeclare/queryWorkUnitYH | 宝鸡、延安、榆林医保资格校验 |
| | POST | /MbDeclare/declareYH | 线下申报(优化) |
| | POST | /MbDeclare/queryDeclareStatusAllYH | 获取系统中全部的申报状态(优化) |
| | POST | /MbDeclare/imageFilesYH | 批量上传图片(优化) |
| | POST | /MbDeclare/queryReviewIcdList | 批量上传图片(优化) |
| | POST | /MbDeclare/ReviewSL | 商洛查询复审病种 |
| **MbDeclareSwitchApi** | POST | /MbDeclareSwitch/MbDeclareSwitch |  |
| | POST | /MbDeclareSwitch/MbDeclareSwitchQuery | 申报开关页面查询 |
| | POST | /MbDeclareSwitch/MbDeclareSwitchAdd | 申报开关页面查询 |
| | POST | /MbDeclareSwitch/MbDeclareSwitchStop | 申报开关页面新增任务 |
| | POST | /MbDeclareSwitch/MbDeclareNoticeQuery | 申报关闭设置停止/删除 |
| | POST | /MbDeclareSwitch/MbDeclareNoticeAdd | 设置通知查询 |
| | POST | /MbDeclareSwitch/MbDeclareNoticeStop | 设置通知新增任务 |
| **MbImportApi** | POST | /MbImport/MbImport |  |
| | POST | /MbImport/query | 慢病信息导入查询分页 |
| | POST | /MbImport/deletefile | (商洛)慢病信息导入信息删除 |
| | POST | /MbImport/uploadMBFile | (商洛)慢病信息导入信息删除 |
| | POST | /MbImport/importMBfile | 慢病信息上传文件 |
| | POST | /MbImport/doErrDownload | 慢病导入 |
| | POST | /MbImport/downloadTemplate | 下载模板(宝鸡) |
| | POST | /MbImport/downloadTemplateDZ | 下载模板(宝鸡) |
| | POST | /MbImport/downloadTemplateSL | 下载模板（达州） |
| | POST | /MbImport/downloadTemplateYH | 下载模板(优化) |
| | POST | /MbImport/updateAndImportMBfile | 慢病导入(上传与导入合并) |
| **MtbDeclareApi** | POST | /declare/declare | 线下申报 |
| | POST | /declare/imageFiles | 批量上传图片 |
| | POST | /declare/queryIcdList | 疾病列表 |
| | POST | /declare/queryWorkUnit | 查询服务窗口 |
| | POST | /declare/getHosList | 根据人员身份获取定点医院 |
| | POST | /declare/YiBaoCheck | 医保资格校验(1101) |
| | POST | /declare/MbCheck | 申报病种校验 |
| | POST | /declare/YbCodeCheck | 医保病种校验(5301) |
| **MtbDeclareCancelApi** | POST | /query/query | 放弃病种列表查询 |
| | POST | /query/queryOnePerson | 单人可放弃病种列表查询 |
| | POST | /query/check | 放弃病种校验 |
| | POST | /query/cancel | 放弃病种 |
| | POST | /query/pictureBinding | 与申请图片绑定 |
| **MtbDeclareExpertAssignApi** | POST | /queryMbDeclarePhysicalCompleteList/queryMbDeclarePhysicalCompleteList | 查询体检完成的申报列表 |
| | POST | /queryMbDeclarePhysicalCompleteList/updateInfo | 专家手动分配撤回 |
| | POST | /queryMbDeclarePhysicalCompleteList/getVipMbDeclareFileByDeclareId | 查询上传资料图片 |
| | POST | /queryMbDeclarePhysicalCompleteList/queryWorkUnit | 查询服务窗口 |
| | POST | /queryMbDeclarePhysicalCompleteList/queryIcdListQEQ | 疾病列表 |
| | POST | /queryMbDeclarePhysicalCompleteList/updateExpertAuto | 专家自动分配（新） |
| | POST | /queryMbDeclarePhysicalCompleteList/updateExpert | 专家手动分配（新） |
| | POST | /queryMbDeclarePhysicalCompleteList/list | 体检分配列表分页查询 |
| | POST | /queryMbDeclarePhysicalCompleteList/physicalAssign | 体检机构手动分配 |
| | POST | /queryMbDeclarePhysicalCompleteList/queryMbExpertList | 查询专家列表 |
| | POST | /queryMbDeclarePhysicalCompleteList/meansBackExpert | 分配专家回退 |
| | POST | /queryMbDeclarePhysicalCompleteList/getDiseaseNameList | 查询慢病信息列表 |
| **MtbDeclareFirstTrialApi** | POST | /queryMbDeclareListInFirstTrail/queryMbDeclareListInFirstTrail | 优化申报资料审核-查询申报列表 |
| | POST | /queryMbDeclareListInFirstTrail/updateMbDeclareFirstApprovalInfo | 优化审批 |
| | POST | /queryMbDeclareListInFirstTrail/getVipMbDeclareFileTypesByDeclareIdYH | 优化查看慢病申报附件分类信息 |
| **MtbDeclareListApi** | POST | /queryList/queryList | 慢病整体优化申报查询 |
| | POST | /queryList/queryWorkUnit | 查询服务窗口(优化) |
| | POST | /queryList/getPictue | 获取图片 |
| | POST | /queryList/getVipMbDeclareFileTypesByDeclareId | 查询上传资料图片 |
| | POST | /queryList/mbGetCredentials | 查看YH审核表 |
| | POST | /queryList/saveVipMbdeclareInfo | 修改YH申报信息 |
| | POST | /queryList/export | 导出(慢病整体优化) |
| | POST | /queryList/credentialsSave | 保存审核表 |
| | POST | /queryList/updateExpertCancel | 专家手动撤回分配（新） |
| | POST | /queryList/queryDetailsList | 慢病整体综合申报查询详情页面查询 |
| | POST | /queryList/downloadBook | pdf文件下载 |
| | POST | /queryList/pdfSave | 保存pdf |
| | POST | /queryList/getPicture | 获取图片信息 |
| | POST | /queryList/getPermission | 获取下载权限 |
| **MtbDeclareSwitchApi** | POST | /MbDeclareSwitchQuery/MbDeclareSwitchQuery | 申报开关页面查询 |
| | POST | /MbDeclareSwitchQuery/MbDeclareSwitchAdd | 申报开关页面查询 |
| | POST | /MbDeclareSwitchQuery/MbDeclareSwitchStop | 申报开关页面新增任务 |
| | POST | /MbDeclareSwitchQuery/MbDeclareNoticeQuery | 申报关闭设置停止/删除 |
| | POST | /MbDeclareSwitchQuery/MbDeclareNoticeAdd | 设置通知查询 |
| | POST | /MbDeclareSwitchQuery/MbDeclareNoticeStop | 设置通知新增任务 |
| **MtbDrugApi** | POST | /queryDrugList/queryDrugList | 慢病药品库管理-查询 |
| | POST | /queryDrugList/queryIcdnameList | 慢病药品库管理-新增按钮-模糊查询疾病名称 |
| | POST | /queryDrugList/insertDrug | 慢病药品库管理-新增按钮-提交药品信息 |
| | POST | /queryDrugList/deleteDrug | 慢病药品库管理-删除按钮-提交药品信息 |
| | POST | /queryDrugList/exportDrug | 慢病药品库管理-导出excel |
| | POST | /queryDrugList/queryImportDrugList | 药品信息导入-药品信息导入查询 |
| | POST | /queryDrugList/downloadDrugMasterplate | 药品信息导入-下载药品导入模板 |
| | POST | /queryDrugList/ImportDrugMessage | 药品信息导入-药品信息导入 |
| | POST | /queryDrugList/ErrDrugDownload | 药品信息导入-药品信息错误下载 |
| | POST | /queryDrugList/queryDrugPlayback | 待发卡管理、慢病人员修改、慢病人员处方修改-药品信息查询回显 |
| **MtbFileApi** | POST | /getPicPath/getPicPath | 获取图片信息 |
| | POST | /getPicPath/getVipMbDeclareFileTypesByDeclareId | 查看慢病申报附件分类信息 |
| **MtbFilingImportRecordApi** | POST | /queryFilingImportRecord/queryFilingImportRecord | 查询备案导入列表 |
| | POST | /queryFilingImportRecord/updateFilingDate | 修改备案享受时间 |
| | POST | /queryFilingImportRecord/deleteFilingRecord | 删除备案数据 |
| | POST | /queryFilingImportRecord/exportFilingRecord | 导出备案记录 |
| | POST | /queryFilingImportRecord/updateDate | 修改备案待遇时间 |
| | POST | /queryFilingImportRecord/getPermission | 验证是否拥有修改待遇享受期权限 |
| **MtbImportApi** | POST | /query/query | 慢病信息导入查询分页 |
| | POST | /query/uploadMBFile | 慢病信息上传文件 |
| | POST | /query/importMBfile | 慢病导入 |
| | POST | /query/doErrDownload | 错误内容下载 |
| | POST | /query/downloadTemplate | 下载模板 |
| | POST | /query/updateAndImportMBfile | 慢病导入(上传与导入合并) |
| | POST | /query/downloadRecordTemplate | 下载备案导入模板 |
| | POST | /query/doErrRecordDownload | 备案导入错误内容下载 |
| | POST | /query/queryRecord | 慢病备案信息导入查询分页 |
| | POST | /query/uploadRecordMBFile | 备案上传文件 |
| **MtbInfoMosaicApi** | POST | /editImage/editImage | 脱敏图片保存 |
| | POST | /editImage/task | 脱敏工作流 |
| | POST | /editImage/getMbDeclareInfo | 资料脱敏查询 |
| | POST | /editImage/restFile | 资料脱敏重置 |
| | POST | /editImage/getVipMbDeclareFileTypesByDeclareId | 查看慢病申报附件分类信息 |
| | POST | /editImage/meansBack | 资料回退 |
| **MtbProfDeclareApi** | POST | /query/query | 查询申报列表 |
| | POST | /query/saveVipMbdeclareApprovalForPart | 保存慢病申报审批表-部分审批功能 |
| | POST | /query/saveVipMbdeclareApproval | 保存慢病申报审批表 |
| | POST | /query/getVipMbDeclareFileTypesByDeclareId | 查询上传资料图片 |
| | POST | /query/getPictue | 获取图片 |
| | POST | /query/getVipMbdeclareFileByDeclareid | 查询体检报告图片 |
| | POST | /query/checkInfoBeforeApproval | 专家审批检查数据 |
| | POST | /query/expertSignatureVo | 用户数据绑定专家签名 |
| **MtbdeclarePhysicalApi** | POST | /list/list | 体检分配列表分页查询 |
| | POST | /list/withdrawDetails | 体检分配详情查询 |
| | POST | /list/queryOrg | 查询体检机构列表 |
| | POST | /list/physicalAssign | 体检机构手动分配 |
| **SxMbDeclareApi** | POST | /vipSxMbDeclare/vipSxMbDeclare |  |
| | POST | /vipSxMbDeclare/YaMbCheck | 陕西申报病种校验 |
| | POST | /vipSxMbDeclare/YlMbCheck | 陕西申报病种校验 |
| | POST | /vipSxMbDeclare/SlMbCheck | 陕西榆林申报病种校验 |
| **VipIntelligentApi** | POST | /intelligent/intelligent |  |
| | POST | /intelligent/getIntelligentInfoByDeclareId | 查询上传图片资料的智能识别结果 |
| | POST | /intelligent/getIntelligentResultByDeclareId | 查询患者智能初审汇总结论 |
| | POST | /intelligent/manualTriggerIntelligentAudit | 手动发起智能审核流程 |
| | POST | /intelligent/saveInconsistencyReason | 保存业务初审复核不一致结论 |
| **VipMBDeclareXcxApi** | POST | /picchealth/picchealth |  |
| | POST | /picchealth/getWeiXinUserStatus | 获取微信用户状态 |
| | POST | /picchealth/updateUserSecretStatus | 更新用户是否阅读过隐私政策的状态 |
| | POST | /picchealth/ForeignUserRegistAndLogin | 第三方用户默认注册登录并绑定关系 |
| | POST | /picchealth/JsonMobileAction | 发送验证码 |
| | POST | /picchealth/queryWorkunit | 查询工作单位 |
| | POST | /picchealth/queryDeclareComList | 查询申报中心地址 |
| | POST | /picchealth/queryIcdList | 疾病列表 |
| | POST | /picchealth/queryIcdListQEQ | 疾病列表 |
| | POST | /picchealth/imageFile | 上传图片 |
| | POST | /picchealth/mbDeclareFile | 申报文件接口 |
| | POST | /picchealth/mbDeclare | 慢病申报 |
| | POST | /picchealth/mbDeclareYa | 慢病申报延安校验规则 |
| | POST | /picchealth/vipCheckAuditForm | 校验领取审核表 |
| | POST | /picchealth/vipQueryAuditFormList | 查询审核表 |
| | POST | /picchealth/queryMBDeclare | 查询申报记录 |
| | POST | /picchealth/queryOneCardList | 查询一卡通列表 |
| | POST | /picchealth/queryNearbyDrugstores | 查询附近药店 |
| | POST | /picchealth/queryUserInfo | 查询用户实名信息 |
| | POST | /picchealth/queryPres | 查询处方信息 |
| | POST | /picchealth/queryReviewDate | 查询处方信息 |
| | POST | /picchealth/getVipMbdeclareFileByDeclareid | 查看体检报告 |
| | POST | /picchealth/updateMobile | 修改手机号 |
| | POST | /picchealth/getDrugstoreInfo | 修改手机号 |
| | POST | /picchealth/getAppIdAndPath | 获取问卷星appId和Path |
| | POST | /picchealth/checkMbDeclare | 校验手机号下是否有申报 |
| | POST | /picchealth/search | 根据药店名或者药品名称搜索 |
| | POST | /picchealth/hotSearch | 热门搜索 |
| | POST | /picchealth/searchDrugs | 热门搜索 |
| | POST | /picchealth/queryDrugRecord | 查询购药记录 |
| | POST | /picchealth/queryBillDetails | 查询账单详情 |
| | POST | /picchealth/getReviewMsg | 获取慢病复审提示信息 |
| | POST | /picchealth/acceptReview | 小程序接受复审 |
| | POST | /picchealth/getHos | 获取定点医院信息 |
| | POST | /picchealth/checkICDDeclareRepeat | 判断是否重复申报高血压和糖尿病 |
| | POST | /picchealth/checkICDDeclareRepeat2 | 判断是否重复申报高血压和糖尿病(仅线下申报和小程序申报调用) |
| | POST | /picchealth/uploadPrescription | 上传处方图片 |
| | POST | /picchealth/uploadPrescriptionYa | 上传处方图片(延安) |
| | POST | /picchealth/VIPUpdatePassword | 会员修改密码接口 |
| | POST | /picchealth/VIPResetPassword | 会员修改密码接口 |
| | POST | /picchealth/download | 生成审批文件并上传FTP |
| | POST | /picchealth/getUploadPrescriptionList | 查询可上传处方图片的申报数据 |
| | POST | /picchealth/getPrescription | 查看处方信息图片 |
| | POST | /picchealth/getYAPrescription | 延安查看处方信息图片 |
| | POST | /picchealth/getYAUpdate | 延安修改处方信息 |
| | POST | /picchealth/rejectPrescriptionImg | 处方驳回 |
| | POST | /picchealth/rejectPrescriptionImgYA | 处方驳回(延安) |
| | POST | /picchealth/orcIdcard | 微信-身份证OCR识别 |
| | POST | /picchealth/ocr5000 | 微信-身份证OCR识别 |
| | POST | /picchealth/getJzmbCredentials | 身份证认证 |
| | POST | /picchealth/downloadnew | 新生成审批文件下载(小程序查数据) |
| | POST | /picchealth/updateApprovaPdf | 新生成审批文件上传(小程序上传生成文件) |
| | POST | /picchealth/sxCheck | 陕西医保资格校验 |
| | POST | /picchealth/slCheck | 陕西医保资格校验 |
| | POST | /picchealth/bjYaYlCheck | 商洛医保资格校验 |
| | POST | /picchealth/getAllCities | 宝鸡、延安、榆林医保资格校验 |
| | POST | /picchealth/bury | 查询所有省市 |
| | POST | /picchealth/xcxBury | 小程序埋点 |
| | POST | /picchealth/downLoadNewSl | 小程序首页埋点 |
| | POST | /picchealth/slCredentialsSave | 保存商洛审核表 |
| | POST | /picchealth/slMbGetCredentials | 保存商洛审核表 |
| | POST | /picchealth/slYearCheck | 查看商洛审核表 |
| | POST | /picchealth/faceRec | 商洛年审提醒 |
| | POST | /picchealth/slAcceptYearCheck | 商洛接受年审 |
| | POST | /picchealth/getUserIdKey | 小程序上传用户姓名身份证的后台 |
| | POST | /picchealth/getInfo | 小程序上传用户姓名身份证的后台 |
| | POST | /picchealth/YaMbCheck | 小程序上传用户姓名身份证的后台 |
| | POST | /picchealth/menu | 陕西病种校验 |
| | POST | /picchealth/queryReviewCode | 小程序目录 |
| | POST | /picchealth/YlMbCheck | 榆林申报病种校验 |
| | POST | /picchealth/SlMbCheck | 榆林申报病种校验 |
| | POST | /picchealth/getSignature | 商洛申报病种校验 |
| | POST | /picchealth/register | 获取h5签名 |
| | POST | /picchealth/loginByIdCard | 小程序身份证号注册 |
| | POST | /picchealth/Yljump | 小程序身份证号登录 |
| | POST | /picchealth/getCity | 榆林小程序跳转 |
| | POST | /picchealth/revertPass | 获取小程序常见问题城市 |
| | POST | /picchealth/updatePass | 小程序身份证号登录重置密码 |
| | POST | /picchealth/uploadPrescriptionYl | 小程序身份证号登录修改密码 |
| | POST | /picchealth/getYLPrescription | 榆林查看处方信息图片 |
| | POST | /picchealth/rejectImgYA | 延安单张处方图片驳回 |
| | POST | /picchealth/getrejectpictureYA | 延安查看处方驳回图片 |
| | POST | /picchealth/getBJPrescriptionPicture | 查看处方图片(宝鸡) |
| | POST | /picchealth/getrejectpictureBJ | 宝鸡查看处方驳回图片 |
| | POST | /picchealth/verifyMobileYA | 延安申报前置手机号校验 |
| | POST | /picchealth/uploadApprovalFileYa | 上传审批表图片(延安) |
| | POST | /picchealth/functionSwitch | 小程序功能开关 |
| | POST | /picchealth/getJkscListing | 健康商城获取列表 |
| | POST | /picchealth/tradingDetails | 健康商城获取列表 |
| | POST | /picchealth/ocrWqx | 健康商城-交易信息保存 |
| | POST | /picchealth/ocrWqxHukouProof | 身份证认证-集团文曲星 |
| | POST | /picchealth/check | 人脸识别查询 |
| | POST | /picchealth/doubleCheck | 人脸识别查询 |
| | POST | /picchealth/xcxVerifyLogin | 人脸识别二次核验 |
| | POST | /picchealth/MPJumpQuery | 零星报销跳转前查询信息（小程序） |
| | POST | /picchealth/reexaminationQuerySL | 零星报销跳转前查询信息（小程序） |
| | POST | /picchealth/declareReviewSL | 商洛复审申报（小程序） |
| | POST | /picchealth/declareReviewSLFile | 商洛复审申报文件接口（小程序） |
| | POST | /picchealth/reexaminationQueryYBSL | 商洛复审信息查询医保接口（小程序） |
| **VipMbDeclareApi** | POST | /rest/vipMbDeclare/rest/vipMbDeclare |  |
| | POST | /rest/vipMbDeclare/vipQueryIcdList | MBD01-慢病管理疾病信息查询 |
| | POST | /rest/vipMbDeclare/vipQueryDeclareComList | MBD02-申报服务中心查询 |
| | POST | /rest/vipMbDeclare/vipMBDeclare | MBD03-慢病申报接口 |
| | POST | /rest/vipMbDeclare/vipMbDeclareFile | MBD04-慢病申报资料上传 |
| | POST | /rest/vipMbDeclare/vipQueryMBDeclare | MBD05-慢病管理申报查询 |
| | POST | /rest/vipMbDeclare/vipQueryMBConsumeFlow | MBD06-慢病管理购药记录查询 |
| | POST | /rest/vipMbDeclare/vipQueryWorkunitForPage | MBD07-慢病管理单位信息查询 |
| | POST | /rest/vipMbDeclare/VipCheckAuditForm | MBD08-慢病管理判断是否有资格领取审核表 |
| | POST | /rest/vipMbDeclare/VipQueryAuditFormList | MBD09-慢病管理领取审核表列表 |
| | POST | /rest/vipMbDeclare/downLoad | MBD10-下载慢病审核表 |
| **VipMbDeclareExpertAssignApi** | POST | /MbDeclareExpertAssign/MbDeclareExpertAssign |  |
| | POST | /MbDeclareExpertAssign/queryMbDeclarePhysicalCompleteList | 查询体检完成的申报列表 |
| | POST | /MbDeclareExpertAssign/querySecond | 专家分歧页查询（宝鸡） |
| | POST | /MbDeclareExpertAssign/updateInfo | 专家手动分配撤回 |
| | POST | /MbDeclareExpertAssign/updateInfoBj | 达州专家手动分配撤回 |
| | POST | /MbDeclareExpertAssign/updateInfoYA | 专家手动分配撤回（宝鸡） |
| | POST | /MbDeclareExpertAssign/updateInfoSL | 专家手动分配撤回(延安) |
| | POST | /MbDeclareExpertAssign/updateInfoYH | 商洛专家手动分配撤回 |
| | POST | /MbDeclareExpertAssign/getVipMbDeclareFileByDeclareId | YH专家手动分配撤回 |
| | POST | /MbDeclareExpertAssign/editImage |  |
| | POST | /MbDeclareExpertAssign/queryMbDeclarePhysicalCompleteListSL | 商洛查询体检完成的申报列表 |
| | POST | /MbDeclareExpertAssign/queryMbDeclarePhysicalCompleteListJZ | 晋中查询体检完成的申报列表 |
| | POST | /MbDeclareExpertAssign/queryMbDeclarePhysicalCompleteListYH | 优化查询体检完成的申报列表 |
| | POST | /MbDeclareExpertAssign/queerySecondIcdYA | 延安专家二次鉴定页面病种查询 |
| **VipMbDeclareFileViewNewApi** | POST | /MbDeclareFileView/MbDeclareFileView |  |
| | POST | /MbDeclareFileView/getVipMbDeclareFileTypesByDeclareId | 查看慢病申报附件分类信息 |
| | POST | /MbDeclareFileView/getPicPath | 获取图片信息 |
| | POST | /MbDeclareFileView/URL5002 | 获取图片信息 |
| | POST | /MbDeclareFileView/getVipMbDeclareFileTypesByDeclareIdSL | 商洛查看慢病申报附件分类信息 |
| | POST | /MbDeclareFileView/getVipMbDeclareFileTypesByDeclareIdYH | 优化查看慢病申报附件分类信息 |
| | POST | /MbDeclareFileView/getVipMbDeclareFileTypesByDeclareIdYL | 查看慢病申报附件分类信息-榆林获取签名图片 |
| **VipMbDeclareFirstTrialApi** | POST | /MbDeclareFirstTrial/MbDeclareFirstTrial |  |
| | POST | /MbDeclareFirstTrial/queryMbDeclareListInFirstTrail | 查询申报列表 |
| | POST | /MbDeclareFirstTrial/queryMbDeclareListInFirstTrailSL | 商洛申报资料审核-查询申报列表 |
| | POST | /MbDeclareFirstTrial/queryMbDeclareListInFirstTrailYH | 优化申报资料审核-查询申报列表 |
| | POST | /MbDeclareFirstTrial/queryMbDeclareListInFirstTrailZJK | 张家口查询申报列表 |
| | POST | /MbDeclareFirstTrial/queryUnitNameType | 查询申报地点列表 |
| | POST | /MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfo | 审批 |
| | POST | /MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfoSL | 商洛审批 |
| | POST | /MbDeclareFirstTrial/updateMbDeclareFirstApprovalInfoYH | 优化审批 |
| | POST | /MbDeclareFirstTrial/updateMbDeclareReviewApprovalInfo | 不予通过 |
| | POST | /MbDeclareFirstTrial/updateMbDeclareReviewApprovalInfoSL | 商洛不予通过 |
| | POST | /MbDeclareFirstTrial/editImage | 商洛不予通过 |
| | POST | /MbDeclareFirstTrial/getHosList | 根据人员身份获取定点医院 |
| | POST | /MbDeclareFirstTrial/saveRemarks | 根据人员身份和病种添加备注 |
| | POST | /MbDeclareFirstTrial/getRemarks | 根据人员身份和病种添加备注 |
| | POST | /MbDeclareFirstTrial/editImageSL | 回显备注 |
| | POST | /MbDeclareFirstTrial/taskSL | 商洛脱敏工作流 |
| | POST | /MbDeclareFirstTrial/getMbDeclareInfoSL | 商洛脱敏工作流 |
| | POST | /MbDeclareFirstTrial/restFileSL | 商洛资料脱敏重置 |
| | POST | /MbDeclareFirstTrial/editImageYH | 商洛资料脱敏重置 |
| | POST | /MbDeclareFirstTrial/taskYH | 优化脱敏图片保存 |
| | POST | /MbDeclareFirstTrial/getMbDeclareInfoYH | 优化脱敏工作流 |
| | POST | /MbDeclareFirstTrial/assignment | 延安自动分配 |
| | POST | /MbDeclareFirstTrial/getProcessing | 校验数据是否正在处理 |
| | POST | /MbDeclareFirstTrial/queryDiseaseMappingList | 查询病种映射列表 |
| | POST | /MbDeclareFirstTrial/editDiseaseMappingList | 新增/编辑/删除病种映射列表 |
| **VipMbDeclareForDocApi** | POST | /Doctor/Doctor |  |
| | POST | /Doctor/query | 查询申报列表 |
| | POST | /Doctor/queryYH | 优化查询申报列表 |
| | POST | /Doctor/nonArrivalPhysical | 未到体检 |
| | POST | /Doctor/giveUp | 未到体检 |
| | POST | /Doctor/getVipMbdeclareFileTypesByDeclareid | 放弃体检 |
| | POST | /Doctor/bookPhysical | 预约体检 |
| | POST | /Doctor/bookPhysicalYH | 预约体检 |
| | POST | /Doctor/uploadPhysicalFile | 预约体检 |
| | POST | /Doctor/uploadPhysicalFileForBatch | 体检报告批量上传 |
| | POST | /Doctor/export | 导出报表 |
| | POST | /Doctor/queryUploadSucc | 查询上传成功列表 |
| | POST | /Doctor/getPhyNote | 获取体检注意事项 |
| **VipMbDeclareForProfApi** | POST | /vipMbDeclareForProf/vipMbDeclareForProf |  |
| | POST | /vipMbDeclareForProf/query | 查询申报列表 |
| | POST | /vipMbDeclareForProf/queryJz | 晋中查询申报列表 |
| | POST | /vipMbDeclareForProf/queryDz | 达州查询申报列表 |
| | POST | /vipMbDeclareForProf/queryYH | 优化查询申报列表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApproval | 保存慢病申报审批表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalBj | 保存慢病申报审批表(宝鸡) |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalJz | 晋中保存慢病申报审批表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalDz | dz保存慢病申报审批表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalForPart | 保存慢病申报审批表-部分审批功能 |
| | POST | /vipMbDeclareForProf/getVipMbdeclareFileTypesByDeclareid | 查询上传资料图片 |
| | POST | /vipMbDeclareForProf/getPictue | 获取图片 |
| | POST | /vipMbDeclareForProf/getVipMbdeclareFileByDeclareid | 查询体检报告图片 |
| | POST | /vipMbDeclareForProf/querySL | 商洛查询申报列表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalSL | 商洛保存慢病申报审批表 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalForPartSL | 商洛保存慢病申报审批表-部分审批功能 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalForPartYH | 优化保存慢病申报审批表-部分审批功能 |
| | POST | /vipMbDeclareForProf/saveVipMbdeclareApprovalYH | 优化保存慢病申报审批表 |
| | POST | /vipMbDeclareForProf/saveMbdeclareApprovalJz | 晋中保存慢病申报审批表（新） |
| | POST | /vipMbDeclareForProf/checkInfoBeforeApproval | 专家审批检查数据（除张家口以外所有地区） |
| | POST | /vipMbDeclareForProf/updatePrescriptionMainForPart | 部分审核通过后修改处方数据(宝鸡) |
| | POST | /vipMbDeclareForProf/rollBackApprovalYl | 榆林撤回专家审核 |
| | POST | /vipMbDeclareForProf/exportProfYL | 专家端导出榆林 |
| | POST | /vipMbDeclareForProf/getPictureByExtId | 榆林-获取专家签名图片 |
| | POST | /vipMbDeclareForProf/queryProf | 榆林-专家端查询专家列表 |
| **VipMbDeclareListApi** | POST | /vipMbDeclareList/vipMbDeclareList |  |
| | POST | /vipMbDeclareList/queryList | 申报查询 |
| | POST | /vipMbDeclareList/queryList2 | 申报修改查询 |
| | POST | /vipMbDeclareList/getVipMbDeclareFileTypesByDeclareId | 查询上传资料图片 |
| | POST | /vipMbDeclareList/getPictue | 获取图片 |
| | POST | /vipMbDeclareList/getVipMbdeclareFileByDeclareid | 查询体检报告图片 |
| | POST | /vipMbDeclareList/export | 导出 |
| | POST | /vipMbDeclareList/exportSL | 导出(商洛) |
| | POST | /vipMbDeclareList/exportXYA | 导出咸阳 |
| | POST | /vipMbDeclareList/exportYH | 导出(慢病整体优化) |
| | POST | /vipMbDeclareList/queryFixedHos | 查询定点医院 |
| | POST | /vipMbDeclareList/queryUnitNameType | 查询一卡通机构名称列表 |
| | POST | /vipMbDeclareList/getVipMbdeclareInfo | 查看慢病申报基础信息 |
| | POST | /vipMbDeclareList/saveVipMbdeclareInfo | 修改申报信息 |
| | POST | /vipMbDeclareList/updateVipMbdeclareInfo | 修改宝鸡发卡前信息 |
| | POST | /vipMbDeclareList/mbCredentialsGet | 查看晋中审核表 |
| | POST | /vipMbDeclareList/JZExpertsDetails | 查看晋中审核表 |
| | POST | /vipMbDeclareList/mbCredentialsSave | 保存晋中审核表 |
| | POST | /vipMbDeclareList/mbCredentials | 保存晋中审核表 |
| | POST | /vipMbDeclareList/jzQueryList | 生成晋中审核表 |
| | POST | /vipMbDeclareList/getAddressAndPresAndReview | 获取地址、复审、处方 |
| | POST | /vipMbDeclareList/downApproval | 获取地址、复审、处方 |
| | POST | /vipMbDeclareList/saveVipMbdeclareInfoSL | 领取上传审批表 |
| | POST | /vipMbDeclareList/saveVipMbdeclareInfoYH | 修改YH申报信息 |
| | POST | /vipMbDeclareList/queryListSL | 商洛申报综合查询 |
| | POST | /vipMbDeclareList/queryListSL2 | 商洛申报综合查询 |
| | POST | /vipMbDeclareList/queryOneSL | 商洛申报单人详细信息查询 |
| | POST | /vipMbDeclareList/queryListCountSL | 商洛数据统计查询 |
| | POST | /vipMbDeclareList/exportCountSl | 商洛数据统计导出 |
| | POST | /vipMbDeclareList/queryListYH | 慢病整体优化申报查询 |
| | POST | /vipMbDeclareList/DetermineConclusion | 确定结论 |
| | POST | /vipMbDeclareList/slCredentialsSave | 保存商洛审核表 |
| | POST | /vipMbDeclareList/slMbGetCredentials | 保存商洛审核表 |
| | POST | /vipMbDeclareList/downloadBook | 查看商洛审核表 |
| | POST | /vipMbDeclareList/slYunWei | 运维商洛限额数据方法 |
| | POST | /vipMbDeclareList/rollBack | 运维商洛限额数据方法 |
| | POST | /vipMbDeclareList/yhMbGetCredentials | 查看YH审核表 |
| | POST | /vipMbDeclareList/yhCredentialsSave | 保存YH审核表 |
| | POST | /vipMbDeclareList/getAdmdvs | 保存YH审核表 |
| | POST | /vipMbDeclareList/updateMobileBj | 查询所有医保区划 |
| | POST | /vipMbDeclareList/getApprovalBj | 修改手机号宝鸡 |
| | POST | /vipMbDeclareList/updateMobileYa | 宝鸡查询专家审核意见 |
| | POST | /vipMbDeclareList/queryListYl | 修改手机号延安 |
| | POST | /vipMbDeclareList/queryListYl2 | 榆林申报查询 |
| | POST | /vipMbDeclareList/queryOneYL | 榆林申报单人详细信息查询 |
| | POST | /vipMbDeclareList/exportYL | 导出榆林 |
| **VipMbDeclareServiceApi** | POST | /mb/auditform/mb/auditform |  |
| | POST | /mb/auditform/query | 查询慢病审核信息 |
| | POST | /mb/auditform/download/{id} | 查询慢病审核信息 |
| **VipMbExpertListApi** | POST | /MbExpertList/MbExpertList |  |
| | POST | /MbExpertList/getIcdFxNameList | 查询阜新病种表慢病信息列表 |
| | POST | /MbExpertList/getIcdNameList | 查询慢病信息列表 |
| | POST | /MbExpertList/getdiseaseYaNameList | 查询延安慢病信息列表 |
| | POST | /MbExpertList/getdiseaseJzNameList | 查询晋中慢病信息列表 |
| | POST | /MbExpertList/queryMbExpertList | 查询专家列表 |
| | POST | /MbExpertList/queryMbExpertListDz | Dz查询专家列表 |
| | POST | /MbExpertList/updateMbDeclareExpertInfo | 专家手动分配 |
| | POST | /MbExpertList/updateMbDeclareExpertInfoBj | 专家手动分配 |
| | POST | /MbExpertList/updateMbDeclareExpertInfoYA | 专家手动分配(宝鸡) |
| | POST | /MbExpertList/assignmentYA | 专家手动分配(延安) |
| | POST | /MbExpertList/updateMbDeclareExpertInfoDz | 批量自动专家分配(延安) |
| | POST | /MbExpertList/queryMbExpertListSL | 专家手动分配DZ |
| | POST | /MbExpertList/updateMbDeclareExpertInfoSL | 商洛专家手动分配 |
| | POST | /MbExpertList/getDiseaseNameListSL | 查询商洛慢病信息列表 |
| | POST | /MbExpertList/AutoMbDeclareExpertInfoSl | 专家自动分配SL |
| | POST | /MbExpertList/updateMbDeclareExpertInfoYH | 优化专家手动分配 |
| | POST | /MbExpertList/getDiseaseNameListYH | 优化专家手动分配 |
| | POST | /MbExpertList/updateExpert | 专家手动分配（新） |
| | POST | /MbExpertList/updateExpertAutoYl | 专家手动分配（新） |
| | POST | /MbExpertList/updateExpertAuto | 专家自动分配（榆林） |
| | POST | /MbExpertList/updateExpertCancel | 专家自动分配（新） |
| | POST | /MbExpertList/updateExpertJz | 专家手动撤回分配（新） |
| | POST | /MbExpertList/updateExpertCancelJz | 晋中专家分配 |
| | POST | /MbExpertList/automaticAllocationSL | 晋中专家撤回分配 |
| | POST | /MbExpertList/automaticAllocationBJ | 宝鸡专家自动分配 |
| | POST | /MbExpertList/automaticAllocationYA | 延安专家自动分配 |
| **XcxDeclareApi** | POST | /queryDeclareComList/queryDeclareComList | 查询申报中心地址 |
| | POST | /queryDeclareComList/queryIcdList | 疾病列表 |
| | POST | /queryDeclareComList/imageFile | 上传图片 |
| | POST | /queryDeclareComList/mbDeclareFile | 申报文件接口 |
| | POST | /queryDeclareComList/mbDeclare | 慢病申报 |
| | POST | /queryDeclareComList/ocr5000 | 身份证认证 |
| | POST | /queryDeclareComList/getAllCities | 查询所有省市 |
| | POST | /queryDeclareComList/getHos | 查询定点医院 |
| | POST | /queryDeclareComList/YiBaoCheck | 医保资格校验(1101) |
| | POST | /queryDeclareComList/MbCheck | 申报病种校验 |
| | POST | /queryDeclareComList/YbCodeCheck | 医保病种校验(5301) |
| | POST | /queryDeclareComList/MbicdcodeCheck | 申报病种校验 |


## 七、数据统计接口 (25个接口)

**模块前缀**: /queryDataStatistics 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **MbDataListApi** | POST | /MbDataList/MbDataList |  |
| | POST | /MbDataList/queryVipCardType | 查询会员卡类型列表 |
| | POST | /MbDataList/queryIcdCodeList | 查询会员卡类型列表 |
| | POST | /MbDataList/queryOutBjHosList | 查询服务列表 |
| | POST | /MbDataList/query |  查询宝鸡的医院信息 |
| | POST | /MbDataList/edit |  查询发卡列表 |
| | POST | /MbDataList/selectGridRow |  保存发卡信息 |
| | POST | /MbDataList/getVipAccountHos |  根据查询条件查询宝鸡药品目录表(已发卡) |
| | POST | /MbDataList/queryBjDrugList |  查询处方信息 |
| | POST | /MbDataList/getPrescription | 查看处方信息图片 |
| **MbDataStatisticsApi** | POST | /MbDataStatistics/MbDataStatistics |  |
| | POST | /MbDataStatistics/queryDataStatisticsYa | 宝鸡数据统计查询 |
| | POST | /MbDataStatistics/StatisticsDataExport | 宝鸡数据统计导出 |
| | POST | /MbDataStatistics/getDataStatisticsYa | 延安数据统计查询 |
| | POST | /MbDataStatistics/StatisticsDataExportYa | 新延安数据统计导出（2023-12-11后） |
| | POST | /MbDataStatistics/StatisticsDataExportYaOld | 旧延安数据统计导出（2023-12-11前） |
| | POST | /MbDataStatistics/getAuth | 账号导出权限查询 |
| **MtbDataStatisticsApi** | POST | /queryDataStatistics/queryDataStatistics | 数据统计查询 |
| | POST | /queryDataStatistics/queryDataStatisticsXYa | 数据统计查询-咸阳 |
| | POST | /queryDataStatistics/statisticsDataExport | 延安数据统计导出 |
| | POST | /queryDataStatistics/statisticsDataExportXYa | 咸阳数据统计导出 |
| **OffLineDetailReportApi** | POST | /query/query | 消费数据查询 |
| | POST | /query/export | 消费数据报表下载 |
| | POST | /query/summary | 线下消费数据汇总查询 |
| | POST | /query/summaryExport | 线下消费数据汇总报表下载 |


## 三、慢病卡管理接口 (52个接口)

**模块前缀**: /opt/vipMbDeclarePhysicalAssign 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **MbmzCardStatusReportApi** | POST | /MbCardStatusReport/MbCardStatusReport |  |
| | POST | /MbCardStatusReport/querySendCardUserList | 商户名称查询 |
| | POST | /MbCardStatusReport/queryDetail | 商户名称查询 |
| | POST | /MbCardStatusReport/export | 查询对账明细 |
| **MbmzInfoHistoryApi** | POST | /MbInfoHistory/MbInfoHistory |  |
| | POST | /MbInfoHistory/queryAccountInfo | 查询会员帐户列表 |
| | POST | /MbInfoHistory/queryHisList | 查询日志 |
| | POST | /MbInfoHistory/queryHisPres | 历史处方查询 |
| | POST | /MbInfoHistory/queryHisHos | 历史医院查询 |
| **MbmzInfoUpdateApi** | POST | /mbmzInfoUpdate/mbmzInfoUpdate |  |
| | POST | /mbmzInfoUpdate/queryAccountInfo | 账户慢病信息表查询 |
| | POST | /mbmzInfoUpdate/updateVipAccountmbmz | 修改账户慢病信息表 |
| | POST | /mbmzInfoUpdate/getVipAccounthosByAccountid | 根据账户ID查看慢病定点医院信息表 |
| | POST | /mbmzInfoUpdate/queryOutBjHosList | 查询宝鸡的医院信息 |
| | POST | /mbmzInfoUpdate/queryIcdName | 疾病信息列表查询 |
| | POST | /mbmzInfoUpdate/getPrescriptionYa | 查看处方信息图片(延安) |
| | POST | /mbmzInfoUpdate/getSelectDrugYA | 修改处方药品信息(延安) |
| | POST | /mbmzInfoUpdate/getInsertDrugYA | 存储处方药品信息(延安) |
| | POST | /mbmzInfoUpdate/getHistoryPrescriptionYa | 存储处方药品信息(延安) |
| | POST | /mbmzInfoUpdate/export | 历史处方信息excel导出 |
| | POST | /mbmzInfoUpdate/uploadPictures | 上传图片(按钮) |
| | POST | /mbmzInfoUpdate/getSelectDoctorYA | 查询开方医生(延安) |
| | POST | /mbmzInfoUpdate/frozenAccount | 慢病卡冻结和解冻(宝鸡) |
| | POST | /mbmzInfoUpdate/getPrescriptionSL | 慢病卡冻结和解冻(宝鸡) |
| | POST | /mbmzInfoUpdate/InsertPresAndDrugSL | 录入处方与药品信息(商洛) |
| | POST | /mbmzInfoUpdate/SelectIcdcodeSL | 处方录入页面查询疾病诊断(商洛) |
| | POST | /mbmzInfoUpdate/getHistoryPrescriptionSl | 查看历史处方信息(商洛) |
| | POST | /mbmzInfoUpdate/exportSL | 历史处方信息excel导出(商洛) |
| | POST | /mbmzInfoUpdate/getDrugSl | 查询用药(商洛) |
| | POST | /mbmzInfoUpdate/SelectDraftSL | 查询草稿(商洛) |
| | POST | /mbmzInfoUpdate/SaveDraftSL | 保存草稿(商洛) |
| | POST | /mbmzInfoUpdate/DeleteDraftSL | 保存草稿(商洛) |
| | POST | /mbmzInfoUpdate/getSelectDrugSL | 删除草稿(商洛) |
| | POST | /mbmzInfoUpdate/getInsertDrugCheckYA | 存储处方药品信息校验(延安) |
| | POST | /mbmzInfoUpdate/getPrescription | 存储处方药品信息校验(延安) |
| | POST | /mbmzInfoUpdate/getPictureResult | ocr处方图片回显 |
| | POST | /mbmzInfoUpdate/getPrescriptionBJ | ocr处方图片识别结果返回 |
| | POST | /mbmzInfoUpdate/BJfilingSynchronize | 备案同步(宝鸡) |
| **MbmzSendCardApi** | POST | /mbmzSendCard/mbmzSendCard |  |
| | POST | /mbmzSendCard/queryForSendWork | 发卡信息查询分页 |
| | POST | /mbmzSendCard/saveVipSendcardForSend | 保存发卡信息 |
| **VipMbdeclareInfoApi** | POST | /vipMbDeclarePhysicalAssign/vipMbDeclarePhysicalAssign |  |
| | POST | /vipMbDeclarePhysicalAssign/list | 体检分配列表分页查询 |
| | POST | /vipMbDeclarePhysicalAssign/details | 体检分配详情查询 |
| | POST | /vipMbDeclarePhysicalAssign/withdrawDetails | 慢病体检撤回分配 |
| | POST | /vipMbDeclarePhysicalAssign/queryOrg | 慢病体检撤回分配 |
| | POST | /vipMbDeclarePhysicalAssign/physicalAssign | 体检机构手动分配 |
| **VipMbdeclareInfoOptApi** | POST | /opt/vipMbDeclarePhysicalAssign/opt/vipMbDeclarePhysicalAssign |  |
| | POST | /opt/vipMbDeclarePhysicalAssign/list | 体检分配列表分页查询 |
| | POST | /opt/vipMbDeclarePhysicalAssign/withdrawDetails | 体检分配列表分页查询 |
| | POST | /opt/vipMbDeclarePhysicalAssign/queryOrg | 慢病体检撤回分配 |
| | POST | /opt/vipMbDeclarePhysicalAssign/physicalAssign | 查询体检机构列表 |


## 九、外部对接接口 (27个接口)

**模块前缀**: /restful/system 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **CallApi** | POST | /call/call |  |
| | POST | /call/list |  |
| | POST | /call/getone |  |
| | POST | /call/getyml |  |
| **RestfulApi** | POST | /restful/system/restful/system |  |
| | GET | /restful/system/info | Restful接口 |
| | POST | /restful/system/healthCheck | Restful接口 |
| **SyncBJMBSBApi** | POST | /SyncBJMBSB/SyncBJMBSB |  |
| | POST | /SyncBJMBSB/SyncDATA | 同步社保数据 |
| **VipMbsbApi** | POST | /rest/vipMbsb/rest/vipMbsb |  |
| | POST | /rest/vipMbsb/mbInfo | MB001-同步慢病备案信息 |
| **WqxOutInterfaceApi** | POST | /WqxOutInterface/WqxOutInterface |  |
| | POST | /WqxOutInterface/pushPicture | 文曲星ocr推送 |
| **WqxStructuredDataApi** | POST | /structured/structured |  |
| | POST | /structured/saveData | ocr推送结构化数据 |
| **XjsApi** | POST | /wqxSeal/wqxSeal | 印章识别 |
| | POST | /wqxSeal/xjsIQI | 图片质检 |
| | POST | /wqxSeal/xjsMIC | 医疗影像分类 |
| | POST | /wqxSeal/xjsMIE | 病案首页信息抽取 |
| | POST | /wqxSeal/xjsIdCardOCR | 身份证识别 |
| | POST | /wqxSeal/xjsMask | 图片脱敏 |
| | POST | /wqxSeal/resetImage | 图片重置接口 |
| | POST | /wqxSeal/queryAutoMaskInfo | 自动脱敏图片回显页面接口 |
| | POST | /wqxSeal/firstTrailPassAutoMask | 初审通过脱敏接口 |
| | POST | /wqxSeal/simpleAutoMask | 单张图片自动脱敏接口 |
| | POST | /wqxSeal/editImage | 单张图片自动脱敏接口 |
| | POST | /wqxSeal/xjsMRX | 处方笺信息抽取 |


## 二、审核管理接口 (36个接口)

**模块前缀**: /MbApprovalFile 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **FaceCheckApi** | POST | /faceCheck/faceCheck |  |
| | POST | /faceCheck/check | 人脸识别查询 |
| | POST | /faceCheck/doubleCheck | 人脸识别查询 |
| **LogAuditApi** | POST | /queryLog/queryLog | 查询审计日志 |
| | POST | /queryLog/addLog | 查询审计日志 |
| **MbApprovalFileApi** | POST | /MbApprovalFile/MbApprovalFile |  |
| | POST | /MbApprovalFile/updateTMbYaApprovalfileService | 延安审批表初审,自动分配专家 |
| | POST | /MbApprovalFile/query | 专家端查询申报列表 |
| | POST | /MbApprovalFile/saveApproval | 专家端审核 |
| | POST | /MbApprovalFile/getApprovalFile | 专家端审核 |
| | POST | /MbApprovalFile/getApprovalFilePicture | 查看审批单图片(延安) |
| | POST | /MbApprovalFile/getApprovalUser | 查看审批单图片(延安) |
| | POST | /MbApprovalFile/getSpecialIcd | 查看专家(延安) |
| | POST | /MbApprovalFile/queryPermissionModification | 延安查询大病 |
| | POST | /MbApprovalFile/EnableDisable | 启用、禁用 |
| | POST | /MbApprovalFile/DistrictQuery | 启用、禁用 |
| **MbReviewApi** | POST | /MbReview/MbReview |  |
| | POST | /MbReview/query | 查询慢病复审记录 |
| | POST | /MbReview/exportReviewList | 慢病复审记录导出 |
| | POST | /MbReview/acceptReview | 慢病复审记录导出 |
| | POST | /MbReview/refuseReview | 接受复审 |
| | POST | /MbReview/acceptReviewBatch | 拒绝复审 |
| **VipMbDeclareDifferenceApi** | POST | /VipMbDeclareDifference/VipMbDeclareDifference |  |
| | POST | /VipMbDeclareDifference/queryMbDeclareDifferenceList | 晋中查询分歧列表 |
| | POST | /VipMbDeclareDifference/query | 晋中查询分歧列表1 |
| | POST | /VipMbDeclareDifference/mbDeclareDifferenceExpertInfo | 晋中查询分歧列表1 |
| **VipMbDeclareReviewApi** | POST | /vipMbDeclareReview/vipMbDeclareReview |  |
| | POST | /vipMbDeclareReview/updateMbdeclareReviewApprovalInfo | 保存慢病申报复审结果和意见 |
| **VipRecordBjApi** | POST | /RecordBj/RecordBj |  |
| | POST | /RecordBj/getRecordBj | 宝鸡慢病备案信息查询 |
| | POST | /RecordBj/ExportRecordBj | 宝鸡慢病备案信息查询 |
| **VipReviewYaApi** | POST | /VipReviewYa/VipReviewYa |  |
| | POST | /VipReviewYa/openAndOff | 复审激活/关闭 |
| | POST | /VipReviewYa/getVipReviewYa | 复审激活/关闭 |
| | POST | /VipReviewYa/vipReviewYaExport | 查看延安专家复审数据 |
| | POST | /VipReviewYa/ReviewSubmit | 导出延安专家复审数据 |


## 五、药店管理接口 (38个接口)

**模块前缀**: /vipDrugstoreChargeList 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **DrugstoreDetailReportApi** | POST | /drugstoreDetailReport/drugstoreDetailReport |  |
| | POST | /drugstoreDetailReport/query | 药店消费明细查询分页 |
| | POST | /drugstoreDetailReport/export | 导出 |
| **DrugstoreOrderPrintApi** | POST | /drugstoreOrderPrint/drugstoreOrderPrint |  |
| | POST | /drugstoreOrderPrint/query | 慢病结算信息报表查询 |
| | POST | /drugstoreOrderPrint/newestQuery | 宝鸡新慢病结算信息报表查询 |
| | POST | /drugstoreOrderPrint/getUser | 获取登录人员 |
| **DrugstoreOrderReportApi** | POST | /drugstoreOrderReport/drugstoreOrderReport |  |
| | POST | /drugstoreOrderReport/query | 药店消费订单信息表查询分页 |
| | POST | /drugstoreOrderReport/queryVipMerchantName | 获取商户名字 |
| | POST | /drugstoreOrderReport/export | 导出 |
| **VipDrugstoreChargeAddApi** | POST | /vipDrugstoreChargeAdd/vipDrugstoreChargeAdd |  |
| | POST | /vipDrugstoreChargeAdd/queryAccountInfoForYD | 药店消费订单信息表查询分页 |
| | POST | /vipDrugstoreChargeAdd/queryDrugstoreProduct | 选择药品 |
| | POST | /vipDrugstoreChargeAdd/getVipAccounthosByAccountid | 查询处方信息和定点医院 |
| **VipDrugstoreChargeAddNewApi** | POST | /vipDrugstoreChargeAddNew/vipDrugstoreChargeAddNew |  |
| | POST | /vipDrugstoreChargeAddNew/queryAccountInfoForYD | 药店消费订单信息表查询分页 |
| | POST | /vipDrugstoreChargeAddNew/queryDrugstoreProduct | 选择药品 |
| | POST | /vipDrugstoreChargeAddNew/getVipAccounthosByAccountid | 查询处方信息和定点医院 |
| **VipDrugstoreChargeListAdminApi** | POST | /vipDrugstoreChargeListAdmin/vipDrugstoreChargeListAdmin |  |
| | POST | /vipDrugstoreChargeListAdmin/queryAccountInfoForYD | 药店消费订单信息表查询分页 |
| | POST | /vipDrugstoreChargeListAdmin/getVipDrugstoreOrder | 查看药店消费订单信息表 |
| | POST | /vipDrugstoreChargeListAdmin/refundVipDrugstoreOrderadmin | 查看药店消费订单信息表 |
| **VipDrugstoreChargeListApi** | POST | /vipDrugstoreChargeList/vipDrugstoreChargeList |  |
| | POST | /vipDrugstoreChargeList/queryAccountInfoForYD | 药店消费订单信息表查询分页 |
| | POST | /vipDrugstoreChargeList/getVipDrugstoreOrder | 查看药店消费订单信息表 |
| **VipDrugstoreOrderApi** | POST | /drugstore/drugstore |  |
| | POST | /drugstore/enter | 缴费管理查询/退费管理查询 |
| | POST | /drugstore/detail | 缴费管理/退费管理查询信息详情 |
| **VipDrugstoreOrderReportApi** | POST | /vipDrugstoreOrderReport/vipDrugstoreOrderReport |  |
| | POST | /vipDrugstoreOrderReport/myVipMerchantName | 获取药店信息 |
| | POST | /vipDrugstoreOrderReport/getDrugstoreOrderReportList | 获取药店信息 |
| | POST | /vipDrugstoreOrderReport/exportDrugstoreOrderReportList | 药店消费订单数据导出 |
| **VipDrugstoreProductListApi** | POST | /vipDrugstoreProductList/vipDrugstoreProductList |  |
| | POST | /vipDrugstoreProductList/queryProductList | 查询药品列表 |
| | POST | /vipDrugstoreProductList/getVipDrugstoreOrder | 查询药品列表 |
| | POST | /vipDrugstoreProductList/updateDrugstoreProductDetail | 修改药品信息查询 |
| | POST | /vipDrugstoreProductList/saveDrugstoreProductDetail | 修改药店药品信息表 |


## 八、系统管理接口 (155个接口)

**模块前缀**: /getWeiXinUserStatus 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **BasedocApi** | POST | /rest/sys/rest/sys |  |
| | POST | /rest/sys/initCallCache | 刷新初始化缓存 |
| | POST | /rest/sys/initGrantMethod | 刷新初始化缓存 |
| | POST | /rest/sys/interfaceGrant | 接口方法配置初始化 |
| **CodeNameApi** | POST | /codename/codename |  |
| | POST | /codename/getCodeName | 根据代码表唯一标识查询codename |
| | POST | /codename/getDistrictCodeList | 省市地区码表查询 |
| | POST | /codename/getCodeList | 获取下拉框信息 |
| | POST | /codename/getPersonType | 人员身份查询 |
| | POST | /codename/getCodes | 人员身份查询 |
| **LeadersApi** | POST | /leader/leader |  |
| | POST | /leader/queryDeclare | 申报慢病情况查询 |
| **LoginApi** | POST | /Login/Login |  |
| | POST | /Login/doLogin | 登录 |
| | POST | /Login/getUser | 登录 |
| | POST | /Login/logOut | 根据登录token获取登录用户信息 |
| | POST | /Login/update | 登出注销 |
| | POST | /Login/updateDz | 修改用户信息 |
| | POST | /Login/signOut | 登出注销 |
| | POST | /Login/getMobile | 登出注销 |
| **MbUserExtApi** | POST | /MbUser/MbUser |  |
| | POST | /MbUser/query | 查询发卡列表 |
| | POST | /MbUser/queryDz | 查询发卡列表 |
| | POST | /MbUser/resetPassword | 重置密码 |
| | POST | /MbUser/DzResetPassword | 重置密码 |
| | POST | /MbUser/UserManageEdit | 重置密码 |
| | POST | /MbUser/userEdit | 编辑获取用户/机构 |
| | POST | /MbUser/DzUserEdit | 编辑用户 |
| | POST | /MbUser/getMbUser | 新增用户 |
| | POST | /MbUser/queryOrgList | 查询体检机构信息 |
| | POST | /MbUser/queryCall1201 | 查询医院机构信息回显 |
| | POST | /MbUser/checkUserAccount | 校验用户名是否存在 |
| | POST | /MbUser/edit | 校验用户名是否存在 |
| | POST | /MbUser/getRole | 新增/修改用户 |
| | POST | /MbUser/getRoleDz | 获取新增用户角色类型下拉 |
| | POST | /MbUser/getExpertDiseases | 获取新增用户角色类型下拉 |
| | POST | /MbUser/querySl | 商洛查询外部管理用户 |
| | POST | /MbUser/queryOrgListSl | 商洛查询体检机构信息 |
| | POST | /MbUser/queryOrgListYh | 优化查询体检机构信息 |
| | POST | /MbUser/UserEditSl | 商洛新增用户 |
| | POST | /MbUser/resetPasswordSl | 商洛新增用户 |
| | POST | /MbUser/UserManageEditSL | 商洛重置密码 |
| | POST | /MbUser/getRoleSl | 获取新增用户角色类型下拉 |
| | POST | /MbUser/getRoleYh | 获取新增用户角色类型下拉 |
| | POST | /MbUser/queryYh | 获取新增用户角色类型下拉 |
| | POST | /MbUser/UserEditYh | YH新增用户 |
| | POST | /MbUser/resetPasswordYh | YH新增用户 |
| | POST | /MbUser/UserManageEditYh | YH重置密码 |
| | POST | /MbUser/EditYh | 编辑获取用户/机构 |
| | POST | /MbUser/unlockAccount | yh编辑用户 |
| | POST | /MbUser/getTemporary | 解锁账号 |
| | POST | /MbUser/getAdmdvs | 查询是否有权限 |
| | POST | /MbUser/userDeleteAccount | 查询医保区划 |
| **MtbExtLoginApi** | POST | /getUser/getUser | 根据登录token获取登录用户信息 |
| | POST | /getUser/update | 修改用户信息 |
| | POST | /getUser/logOut | 登出注销 |
| **MtbUserExtApiAndOrg** | POST | /query/query | 查询外部管理用户 |
| | POST | /query/getDiseaseNameList | 查询慢病信息列表 |
| | POST | /query/unlockAccount | 解锁账号 |
| | POST | /query/getDistrictCodeList | 省市地区码表查询 |
| | POST | /query/addPhysicalOrg | 新增体检站点 |
| | POST | /query/getRole | 获取新增用户角色类型下拉 |
| | POST | /query/queryOrgList | 优化查询体检机构信息 |
| | POST | /query/getCodes | 码表查询 |
| | POST | /query/UserEdit | 新增用户 |
| | POST | /query/resetPassword | 重置密码 |
| | POST | /query/UserManageEdit | 编辑获取用户/机构 |
| | POST | /query/Edit | 编辑用户 |
| | POST | /query/queryCall1201 | 查询医院机构信息回显 |
| | POST | /query/userDeleteAccount | 删除用户 |
| **PersonDivisionApi** | POST | /personDivision/personDivision |  |
| | POST | /personDivision/getServiceWindowAndPersonType | 人员地区身份划分 |
| **SchedulingApi** | POST | /scheduling/scheduling |  |
| | POST | /scheduling/ghiInsureDetailInitTask | 执行GhiInsureDetailInitTask任务 |
| | POST | /scheduling/BJRecordTask | 宝鸡慢病备案信息查询 |
| | POST | /scheduling/BJDelFilingTask | 宝鸡同步病种删除 |
| | POST | /scheduling/vipMbmzStatusTask | 执行vipMbmzStatusTask任务 |
| | POST | /scheduling/vipMbmzUpdateTask | 执行vipMbmzUpdateTask任务 |
| | POST | /scheduling/vipSendMessageTask | 执行vipSendMessageTask任务 |
| | POST | /scheduling/vipReviewGetPhysicalTask | 执行vipReviewGetPhysicalTask任务 |
| | POST | /scheduling/vipMbdeclareGetPhysicalTask | 执行vipMbdeclareGetPhysicalTask任务 |
| | POST | /scheduling/reviewWaringTask | 执行ReviewWaringTask任务 |
| | POST | /scheduling/drugSynchronizedTask | 执行同步健医购药订单药品信息 |
| | POST | /scheduling/bjMedicPutOnRecTask | 执行宝鸡的数据在陕西医保备案bjMedicPutOnRecTask任务 |
| | POST | /scheduling/slMedicPutOnRecTask | 执行商洛的数据在陕西医保备案slMedicPutOnRecTask任务 |
| | POST | /scheduling/yaMedicPutOnRecTask | 执行延安的数据在陕西医保备案yaMedicPutOnRecTask任务 |
| | POST | /scheduling/ylMedicPutOnRecTask | 执行榆林的数据在陕西医保备案ylMedicPutOnRecTask任务 |
| | POST | /scheduling/YLIMedicPutOnRecTask | 执行杨凌的数据在陕西医保备案yliMedicPutOnRecTask任务 |
| | POST | /scheduling/xyaMedicPutOnRecTask | 执行咸阳的数据在陕西医保备案yliMedicPutOnRecTask任务 |
| | POST | /scheduling/bjMedicPORResearchTask | 执行宝鸡在陕西医保备案数据查询bjMedicPORResearchTask任务 |
| | POST | /scheduling/slMedicPORResearchTask | 执行商洛在陕西医保备案数据查询slMedicPORResearchTask任务 |
| | POST | /scheduling/yaMedicPORResearchTask | 执行延安在陕西医保备案数据查询yaMedicPORResearchTask任务 |
| | POST | /scheduling/ylMedicPORResearchTask | 执行榆林在陕西医保备案数据查询ylMedicPORResearchTask任务 |
| | POST | /scheduling/YLIMedicPORResearchTask | 执行杨凌在陕西医保备案数据查询YLIMedicPORResearchTask任务 |
| | POST | /scheduling/xyaMedicPORResearchTask | 执行咸阳在陕西医保备案数据查询xyaMedicPORResearchTask任务 |
| | POST | /scheduling/wqxOutInterfaceTask | 执行文曲星OCR任务 |
| | POST | /scheduling/xjsMRXOutInterfaceTask | 宝鸡-发起处方笺识别 |
| | POST | /scheduling/approval2EndYl | 榆林推送工作流 |
| | POST | /scheduling/file2ImageTask | 执行File2Image任务 |
| | POST | /scheduling/icdExpiresTask | 执行IcdExpiresTask任务 |
| | POST | /scheduling/slYearCheckTask | 执行商洛年审任务 |
| | POST | /scheduling/vipAccountMoneyResetTask | 执行VipAccountMoneyResetTask任务 |
| | POST | /scheduling/slYearPostponeTask | 执行商洛年审享受时间延期任务 |
| | POST | /scheduling/BJAutoFilingTask | 宝鸡慢病自动备案 |
| | POST | /scheduling/jcSendMessageTask | 执行晋城短信定时任务 |
| | POST | /scheduling/repeatedRequestsTask | 执行宝鸡共享库接口重复请求定时任务：执行repeatedRequestsTask任务 |
| | POST | /scheduling/detectionSwitchTask | 执行宝鸡共享库处方查询开关检测定时任务：执行detectionSwitchTask任务 |
| | POST | /scheduling/imageQualityInspectionTaskBJ | 慢病初审智能化图片质检定时任务(宝鸡) |
| | POST | /scheduling/updateAccountEnableTask | 禁止过期账号 |
| | POST | /scheduling/imageQualityRuleValidationTaskBJ | 慢病初审智能化图片质检规则校验定时任务(宝鸡) |
| | POST | /scheduling/medicalImageClassificationTaskBJ | 慢病初审智能化医疗影像分类定时任务(宝鸡) |
| | POST | /scheduling/micRuleValidationTaskBJ | 慢病初审智能化医疗影像分类规则校验定时任务(宝鸡) |
| | POST | /scheduling/idCardOcrTaskBJ | 慢病初审智能化身份证识别定时任务(宝鸡) |
| | POST | /scheduling/idCardOcrRuleValidationTaskBJ | 慢病初审智能化身份证识别规则校验定时任务(宝鸡) |
| | POST | /scheduling/sealRecognitionTaskBJ | 慢病初审智能化印章识别定时任务(宝鸡) |
| | POST | /scheduling/sealRecognitionRuleValidationTaskBJ | 慢病初审智能化印章识别规则校验定时任务(宝鸡) |
| | POST | /scheduling/medicalInfoExtractionTaskBJ | 慢病初审智能化病案首页信息抽取定时任务(宝鸡) |
| | POST | /scheduling/medicalInfoExtractionRuleValidationTaskBJ | 慢病初审智能化病案首页信息抽取规则校验定时任务(宝鸡) |
| | POST | /scheduling/imageAutoMaskTaskBJ |  |
| **VipJkdaApi** | POST | /jkdaService/jkdaService |  |
| | POST | /jkdaService/getPhysicalAndUPReport | QUERYREPORT 获取体检报告修改体检信息 |
| | POST | /jkdaService/getPhysicalAndUPReportRe | QUERYREPORT 获取复审体检报告修改体检信息 |
| | POST | /jkdaService/getPhysicalReport | QUERYREPORT 获取体检报告 |
| | POST | /jkdaService/getPhysicalReportRe | QUERYREPORT (宝鸡专家端)获取复审体检报告 |
| **VipOrgBankinfoApi** | POST | /vipOrgBankinfo/vipOrgBankinfo |  |
| | POST | /vipOrgBankinfo/query | 服务机构的银行信息表查询 |
| | POST | /vipOrgBankinfo/save | 保存服务机构的银行信息表 |
| **VipPhysicalOrgApi** | POST | /PhysicalOrg/PhysicalOrg |  |
| | POST | /PhysicalOrg/getPhysicalOrgList | 查询体检站点列表 |
| | POST | /PhysicalOrg/addPhysicalOrg | 新增体检站点 |
| | POST | /PhysicalOrg/addPhysicalOrgYh | yh新增体检站点 |
| | POST | /PhysicalOrg/updateStatus | 体检站点状态更改 |
| **XcxIndexApi** | POST | /queryUserInfo/queryUserInfo | 查询用户实名信息 |
| | POST | /queryUserInfo/queryNearbyDrugstores | 查询附近药店 |
| | POST | /queryUserInfo/queryMBDeclare | 查询申报记录 |
| | POST | /queryUserInfo/updateMobile | 修改手机号 |
| | POST | /queryUserInfo/getUploadPrescriptionList | 查询可上传处方图片的申报数据 |
| | POST | /queryUserInfo/uploadPrescription | 上传处方图片 |
| | POST | /queryUserInfo/vipCheckAuditForm | 校验领取审核表 |
| | POST | /queryUserInfo/vipQueryAuditFormList | 查询审核表 |
| | POST | /queryUserInfo/downloadnew | 新生成审批文件下载(小程序查数据) |
| | POST | /queryUserInfo/queryBillDetails | 查询账单详情 |
| | POST | /queryUserInfo/queryOneCardList | 查询一卡通列表 |
| | POST | /queryUserInfo/VIPResetPassword | 会员重置密码接口 |
| | POST | /queryUserInfo/VIPUpdatePassword | 会员修改密码接口 |
| | POST | /queryUserInfo/getPrescriptionPicture | 查看处方图片 |
| | POST | /queryUserInfo/getVipMbdeclareFileByDeclareid | 查看体检报告 |
| | POST | /queryUserInfo/getRejectPicture | 查看驳回处方图片与驳回原因 |
| | POST | /queryUserInfo/notificationListing | 治疗通知单列表 |
| | POST | /queryUserInfo/notificationDownload | 治疗通知单下载（小程序） |
| | POST | /queryUserInfo/notificationPdfSave | 治疗通知单保存（小程序） |
| **XcxLoginApi** | POST | /getWeiXinUserStatus/getWeiXinUserStatus | 获取微信用户状态 |
| | POST | /getWeiXinUserStatus/updateUserSecretStatus | 更新用户是否阅读过隐私政策的状态 |
| | POST | /getWeiXinUserStatus/ForeignUserRegistAndLogin | 第三方用户默认注册登录并绑定关系 |
| | POST | /getWeiXinUserStatus/JsonMobileAction | 发送验证码 |


## 六、费用管理接口 (32个接口)

**模块前缀**: /vipAccount 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **MbMzSettlementReportApi** | POST | /MbSettlementReport/MbSettlementReport |  |
| | POST | /MbSettlementReport/query | 查询对账明细列表 |
| | POST | /MbSettlementReport/export | 查询对账明细列表 |
| **VipAccountApi** | POST | /ppop/ppop | 支付平台线下缴费 |
| | POST | /ppop/querylist | 查询缴费列表 |
| **VipAccountDataApi** | POST | /vipAccountDataList/vipAccountDataList |  |
| | POST | /vipAccountDataList/queryList | 条件查询慢病卡列表 |
| | POST | /vipAccountDataList/export | 条件查询慢病卡列表 |
| | POST | /vipAccountDataList/mergeAccount | 慢病卡合卡 |
| **VipAccountInfoApi** | POST | /vipAccount/vipAccount |  |
| | POST | /vipAccount/queryVipCardType | 查询会员卡类型列表 |
| | POST | /vipAccount/queryVipGradeType | 查询会员卡类型列表 |
| | POST | /vipAccount/queryAccountInfo | 查询会员级别列表 |
| | POST | /vipAccount/qureyFLowDetailList | 查询会员帐户列表 |
| | POST | /vipAccount/queryFLowDetail | 查看会员消费流水 |
| | POST | /vipAccount/cardActive | 取得费用信息 |
| | POST | /vipAccount/cardAgainActive | 卡激活 |
| **VipAccountMbmzListApi** | POST | /vipAccountMbmzList/vipAccountMbmzList |  |
| | POST | /vipAccountMbmzList/getVipAccountmbmzListForView | 账户慢病信息表查询分页 |
| | POST | /vipAccountMbmzList/updateStatus | 服务状态修改 |
| | POST | /vipAccountMbmzList/VIPUpdatePassword | 会员修改密码接口 |
| | POST | /vipAccountMbmzList/VIPResetPassword | 会员修改密码接口 |
| **VipChronicPayApi** | POST | /rest/VipChronicAccount/rest/VipChronicAccount |  |
| | POST | /rest/VipChronicAccount/VIPAuthChronic | 慢病会员卡进行身份认证 |
| | POST | /rest/VipChronicAccount/VIPQueryChronicBalance | 查询慢病会员卡余额功能 |
| | POST | /rest/VipChronicAccount/VIPChronicPay | 会员消费金额 |
| | POST | /rest/VipChronicAccount/VIPChronicRefund | 会员账户金额消费退还 |
| | POST | /rest/VipChronicAccount/VIPChronicPayCallback | 会员消费金额回调接口 |
| | POST | /rest/VipChronicAccount/VIPUpdatePassword | 会员修改密码接口 |
| **VipMoneyFlowSelectApi** | POST | /vipMoneyFlowSelect/vipMoneyFlowSelect |  |
| | POST | /vipMoneyFlowSelect/qureyFLowDetailList | 消费明细查询分页 |
| | POST | /vipMoneyFlowSelect/qureyProductFlowDetail | 账户消费明细列表 |


## 十、工作流接口 (7个接口)

**模块前缀**: /activiti6 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **Activiti6Api** | POST | /activiti6/activiti6 |  |
| | POST | /activiti6/deploy | 工作流发布 |
| **ActivitiApi** | POST | /activiti/activiti |  |
| | POST | /activiti/addComment | 添加备注 |
| | POST | /activiti/getComments | 添加备注 |
| | POST | /activiti/getHistories | 查询备注列表 |
| | POST | /activiti/meansBack | 查询操作轨迹列表 |


## 四、处方管理接口 (87个接口)

**模块前缀**: /getPrescription 等

| 类名 | HTTP | 路径 | 说明 |
|------|------|------|------|
| **CxPrescriptionPoolApi** | POST | /cxPrescription/cxPrescription |  |
| | POST | /cxPrescription/prePoolExit | 1.5处方池注销 |
| | POST | /cxPrescription/prePoolIncrease | 1.5处方池注销 |
| | POST | /cxPrescription/recordInsert | 1.4处方池新增 |
| | POST | /cxPrescription/recordLogout | 1.1 备案新增 |
| | POST | /cxPrescription/recordInquire | 1.2 备案注销 |
| | POST | /cxPrescription/recordInsertbj | 1.3 备案查询 |
| **MbPrescriptionManagementApi** | POST | /MbPrescriptionManagement/MbPrescriptionManagement |  |
| | POST | /MbPrescriptionManagement/getYLPrescriptionPicture | 查看处方图片(榆林) |
| | POST | /MbPrescriptionManagement/InsertDrugYL | 存储处方药品信息(榆林) |
| | POST | /MbPrescriptionManagement/UpdateButtonYL | 存储处方药品信息(榆林) |
| | POST | /MbPrescriptionManagement/getPrescriptionYl | 处方录入完成按钮(榆林) |
| | POST | /MbPrescriptionManagement/export | 历史处方信息excel导出(榆林) |
| | POST | /MbPrescriptionManagement/getHistoryPrescriptionYl | 查看历史处方信息(榆林) |
| | POST | /MbPrescriptionManagement/rejectPrescriptionImgYL | 处方驳回(榆林) |
| | POST | /MbPrescriptionManagement/getSelectDrugYL | 模糊查询药品名称(榆林) |
| | POST | /MbPrescriptionManagement/getBJPrescriptionPicture | 查看处方图片(宝鸡) |
| | POST | /MbPrescriptionManagement/InsertDrugBJ | 存储处方药品信息(宝鸡) |
| | POST | /MbPrescriptionManagement/UpdateButtonBJ | 存储处方药品信息(宝鸡) |
| | POST | /MbPrescriptionManagement/rejectPrescriptionImgBJ | 处方录入完成按钮(宝鸡) |
| | POST | /MbPrescriptionManagement/getSelectDrugBJ | 模糊查询药品信息(宝鸡) |
| | POST | /MbPrescriptionManagement/getHistoryPrescriptionBj | 查看历史处方信息(宝鸡) |
| | POST | /MbPrescriptionManagement/exportBjHistory | 历史处方信息excel导出(榆林) |
| | POST | /MbPrescriptionManagement/updateHistoryDrugYA | 修改历史处方药品信息(延安) |
| | POST | /MbPrescriptionManagement/rejectPreImgBJ | 修改历史处方药品信息(延安) |
| | POST | /MbPrescriptionManagement/checkPicture | 处方单张驳回(宝鸡) |
| | POST | /MbPrescriptionManagement/uploadPrescriptionPC | 待发卡页面-校验是否存在处方图片(宝鸡) |
| **MtbPrescriptionManagementApi** | POST | /getPrescription/getPrescription | 处方管理页面-查询处方信息 |
| | POST | /getPrescription/getPictureResult | 处方管理页面-查看按钮-ocr处方图片识别结果返回 |
| | POST | /getPrescription/getInsertDrugCheck | 处方管理页面-查看按钮-存储处方药品信息校验 |
| | POST | /getPrescription/getOCRPrescription | 处方管理页面-查看按钮-ocr处方图片数据回显 |
| | POST | /getPrescription/getDrugForm | 处方管理页面-查看按钮-查看药品剂型 |
| | POST | /getPrescription/getSelectDrug | 处方管理页面-查看按钮-查询药品名称 |
| | POST | /getPrescription/getSelectDoctor | 处方管理页面-查看按钮-查询开方医生 |
| | POST | /getPrescription/insertDrug | 处方管理页面-查看按钮-存储处方药品信息 |
| | POST | /getPrescription/updateFinishButton | 处方管理页面-查看按钮-完成按钮 |
| | POST | /getPrescription/rejectSingleImg | 处方管理页面-查看按钮-单张处方图片驳回 |
| | POST | /getPrescription/rejectBatchImg | 处方管理页面-查看按钮-批量处方图片驳回 |
| | POST | /getPrescription/getHistoryPrescription | 处方管理页面-历史录入处方查看按钮 |
| | POST | /getPrescription/imagePrescriptionFilePC | 处方管理页面-处方上传/查看按钮-上传图片 |
| | POST | /getPrescription/uploadPrescriptionPC | 处方管理页面-处方上传/查看按钮-提交图片 |
| | POST | /getPrescription/InsertDrugPC | 处方管理页面-处方录入按钮-提交处方药品信息PC端 |
| | POST | /getPrescription/getPrescriptionPictruePC | 处方管理页面-处方上传/查看按钮-查看pc端上传的图片接口 |
| | POST | /getPrescription/updateHistoryDrug | 处方管理页面-修改历史处方药品信息 |
| | POST | /getPrescription/exportHistoryPrescriptionDrug | 处方管理页面-历史处方信息excel导出 |
| | POST | /getPrescription/queryDiseaseTypes | 处方管理页面-查询疾病类型 |
| | POST | /getPrescription/getPrescriptionXYA | 处方管理页面-查询处方信息 |
| | POST | /getPrescription/exportXYAHistoryPrescriptionDrugXYA | 处方管理页面-历史处方信息excel导出 |
| | POST | /getPrescription/getPrescriptionPictureXYA | 查看处方图片 |
| | POST | /getPrescription/getHistoryPrescriptionXYA | 处方管理页面-历史录入处方查看按钮 |
| | POST | /getPrescription/getDrugFormXYA | 处方管理页面-查看按钮-查看药品剂型 |
| | POST | /getPrescription/getPictureResultXYA | 处方管理页面-查看按钮-新技术处图片识别结果返回 |
| | POST | /getPrescription/rejectSingleImgXYA | 处方管理页面-查看按钮-单张处方图片驳回 |
| | POST | /getPrescription/rejectBatchImgXYA | 处方管理页面-查看按钮-批量处方图片驳回 |
| | POST | /getPrescription/updateFinishButtonXYA | 处方管理页面-查看按钮-完成按钮 |
| | POST | /getPrescription/InsertDrugPCXYA | 处方管理页面-处方录入按钮-提交处方药品信息PC端 |
| | POST | /getPrescription/updateHistoryDrugXYA | 处方管理页面-修改历史处方药品信息 |
| | POST | /getPrescription/getSelectDrugXYA | 处方管理页面-查看按钮-查询药品名称 |
| | POST | /getPrescription/getOCRPrescriptionXYA | 处方管理页面-查看按钮-ocr处方图片数据回显 |
| | POST | /getPrescription/getInsertDrugCheckXYA | 处方管理页面-查看按钮-存储处方药品信息校验 |
| | POST | /getPrescription/insertDrugXYA | 处方管理页面-查看按钮-存储处方药品信息 |
| **PrescriptionPoolApi** | POST | /queryPreBj/queryPreBj | 购药系统查询处方（宝鸡） |
| **VipPrescriptionApi** | POST | /MbPrescription/MbPrescription |  |
| | POST | /MbPrescription/uploadandimportFileYa | 延安处方文件上传与导入 |
| | POST | /MbPrescription/doErrDownloadYa | 延安处方错误内容下载 |
| | POST | /MbPrescription/addData | 25万数据存储 |
| | POST | /MbPrescription/uploadPrescriptionYa | 25万数据存储 |
| | POST | /MbPrescription/getYAPrescription | 延安处方上传 |
| | POST | /MbPrescription/testQuery | 延安查看处方 |
| | POST | /MbPrescription/drugExport | 测试查询 |
| | POST | /MbPrescription/queryYA | 延安处方池用药目录导出查询 |
| | POST | /MbPrescription/getDrugYa | 查看用药目录 |
| | POST | /MbPrescription/getDrugPrescriptionYa | 查看处方信息 |
| | POST | /MbPrescription/InsertDrugYA | PC端录入处方药品信息(延安) |
| | POST | /MbPrescription/getDrugForm | PC端录入处方药品信息(延安) |
| **YaPrescriptionPoolApi** | POST | /prescription/prescription |  |
| | POST | /prescription/pushdata | YARBCXCF01-人保财险处方系统推送接口 |
| | POST | /prescription/queryPre | 购药系统查询处方 |
| | POST | /prescription/queryPreBj | 购药系统查询处方 |
| | POST | /prescription/prescriptionTransfer | 购药系统查询处方（宝鸡） |
| | POST | /prescription/prescriptionFeedbackBj | 宝鸡购药系统处方信息回传接口 |
| | POST | /prescription/queryPreYLI | 购药系统查询处方 |
| | POST | /prescription/queryPreXYA | 购药系统查询处方 |
| | POST | /prescription/getOrderBJ | 购药系统查询处方(咸阳) |
| | POST | /prescription/queryOrderBJ | 打印结算单核对购药订单数量接口(宝鸡) |
| | POST | /prescription/queryPreSL | 购药系统查询处方（商洛） |
| | POST | /prescription/prescriptionTransferXYA | 购药系统查询处方（商洛） |

---
## 附录

### 文档说明
- **统计口径**: 包含所有Java API类中的HTTP接口方法
- **路径格式**: 类级别@RequestMapping + 方法级别路径
- **脱敏处理**: 已对可能存在的敏感信息进行脱敏

### 未分类接口

| 类名 | 路径 | 接口数 |
|------|------|--------|
| DpViewApi | /dpViewQuery | 7 |
| FilingManApi | /filingMan | 5 |
| MbUpdateApi | /MbUpdate | 5 |
| MbYearCheckApi | /MbYearCheck | 4 |
| MtbUpdateApi | /updatequery | 5 |
| OpsApi | /ops | 11 |
| TFilingManApi | /queryFiling | 4 |
| TMbRecordApi | /tMbRecord | 2 |
| TestApi | /test | 5 |
| TestEncryptApi | /update | 2 |
| VipMbmzStatusLogListApi | /vipMbmzStatusLogList | 3 |

---

📎 **延伸阅读**：
- [申报流程解析](picc-mzmtb-server-申报流程解析.md) - 详细了解申报管理接口(435个)对应的业务流程
- [数据模型解析](picc-mzmtb-server-数据模型解析.md) - API背后对应的数据库表结构和Mapper XML
- [处方与药店管理解析](picc-mzmtb-server-处方与药店管理解析.md) - 处方管理(87接口)和药店管理(38接口)的详细说明
