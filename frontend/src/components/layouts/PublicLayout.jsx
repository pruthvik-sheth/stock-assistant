import { AppPath } from '@/contants/AppPath';
import { useCurrentUser } from '@/hooks/zustand/useCurrentUser';
import { Navigate, Outlet } from 'react-router-dom';

export const PublicLayout = () => {
    const isAuthenticated = useCurrentUser((state) => state.isAuthenticated);

    if (isAuthenticated) {
        return <Navigate to={AppPath.Home} />;
    }

    return (
        <div className='grid grid-cols-2 w-screen h-screen'>
            <div className='flex flex-row items-center justify-center'>
                <Outlet />
            </div>
            <div className='flex flex-row items-center justify-center bg-red-50'>
                {/* <BrandWordMark className='w-1/2' /> */}
                <h1 className='text-7xl font-black'>QuantAI</h1>
            </div>
        </div>
    );
};