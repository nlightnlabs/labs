
export const appName = 'SaaS App';

export const author="nlightn Labs";

export const version = '1.0.0';

interface AppItem{
    id: string;
    section: string;
    name: string;
    label: string;
    description: string;
    icon_url_path: string;
    path: string;
}


export const sideBarItems: AppItem[] = [
    {id: '0', section:"General", name: 'chat', label: 'nav.chat', description: 'AI Chat Assistant', icon_url_path: '/icons/chat.svg', path: '/chat'},
    {id: '1', section:"General", name: 'data', label: 'nav.data', description: 'Manage Data', icon_url_path: '/icons/data.svg', path: '/data'},
    {id: '2', section:"Applications", name: 'app1', label: 'nav.app1', description: 'Description for Application 1', icon_url_path: '/icons/app1.svg', path: '/app1'},
    {id: '3', section:"Applications", name: 'app2', label: 'nav.app2', description: 'Description for Application 2', icon_url_path: '/icons/app2.svg', path: '/app2'},
    {id: '4', section:"Applications", name: 'app3', label: 'nav.app3', description: 'Description for Application 3', icon_url_path: '/icons/app3.svg', path: '/app3'}
]
