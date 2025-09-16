export const getRedirection = (
  isCurrentWorkspaceEditor: boolean,
  app: any, redirectionFunc: (href: string) => void,
  activeArea?: number | undefined,
) => {
  switch (app.mode) {
    case 'workflow':
    case 'advanced-chat':
    case 'metabolic':
    case 'advanced-chat':
      // console.log("121212", app.mode)
      redirectionFunc(`/app/${app.id}/workflow?status=${app?.status}&tabClick=${app?.tabClick}&tenant_id=${app.tenant_id}&category=${app.category}&name=${app.name}&fromType=${app?.fromType}`);
      break;
    case 'chat':
      if (app.status !== 'installed') {
        redirectionFunc(`/tools/createByUrl?original_provider=${app.name}&desc=${app.desc}&tenant_id=${app.tenant_id}`);
      }
      break;
    case 'agent-chat':
      if (app.name && app.category && app.appId) {
        redirectionFunc(`/app/${app.id}/configuration?status=${app?.status}&fromType=${app?.fromType}&tabClick=${app?.tabClick}&tenant_id=${app.tenant_id}&name=${app.name}&category=${app.category}&appId=${app.appId}`);
      } else {
        redirectionFunc(`/app/${app.id}/configuration?tenant_id=${app.tenant_id}&fromType=${app?.fromType}&tabClick=${app?.tabClick}&appId=${app.appId}&desc=${app.desc}`);
      }
      break;
    case 'workSpaceSecondPage':
      redirectionFunc(`/apps?category=workSpaceSecondPage&tenant_id=${app.tenant_id}&role=${app.role}&name=${app.name}`);
      break;
    case 'project-member':
      redirectionFunc(`/apps?category=project-member&role=${app.role}&tenant_id=${app.tenant_id}`);
      break;
    case 'appExamine':
      redirectionFunc(`/apps?category=appExamine&breadcrumb=${app.breadcrumb}&role=${app.role}&tenant_id=${app.tenant_id}`);
      break;
    case 'editAuthority':
      redirectionFunc(`/apps?category=editAuthority&params=${app.params}&tenant_id=${app.tenant_id}&status=${app.status}&role=${app.role}`);
      break;
    default:
      return false;
  }
}
